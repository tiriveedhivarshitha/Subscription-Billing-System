from fastapi import APIRouter, HTTPException, Depends
from database.oracleDBconnection import get_connection
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydanticModel import products, planRecord, CustomerRecord, PlanUpdate, subscriptionValidation, customerDetails
from database.oracleDBconnection import get_connection, get_admin_key, get_secret_key
from pydantic import BaseModel
import json
from datetime import datetime, timedelta
import jwt
import random
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler


app = APIRouter()
"""DECODING THE CUSTOMER_ID FROM THE JWT TOKEN"""
security = HTTPBearer() 
# 2. Update the function to use the new security scheme
def get_current_customer(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # MAGIC: HTTPBearer automatically removes the word "Bearer " for you! 
        # So we don't need to use .split(" ") anymore.
        token = credentials.credentials 
        SECRET_KEY=get_secret_key()
        payload = jwt.decode(token,  algorithms=["HS256"])
        return payload["customer_id"]
        
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Token")

####################################### CREATING CUSTOMER MANAGEMENT API'S ################################################



""" UPDATE CUSTOMER API"""
@app.patch("/update/customers/{customer_id}")
def update_customer(customer_id:str, customer_details:customerDetails):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        data = customer_details.model_dump(exclude_unset=True)
        for key, value in data.items():
            cursor.execute(
                        f"""
                        UPDATE customers
                        SET {key} = :1
                        WHERE customer_id = :2
                        """,
                        [value, customer_id]
                    )
        cursor.execute(""" update customers
                            set updated_at= :1
                            where customer_id= :2""",
                            [datetime.now(),customer_id], 
                            )
        connection.commit()
        return {"message": "Plan updated successfully"}
        
    finally:
        cursor.close()
        connection.close()
    


@app.put("/subscription/status")
def status_update(status_record: subscriptionValidation, customer_id: str = Depends(get_current_customer)):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        """VALID STATUS TRANSITIONS
           trial -> active
           trial -> cancelled
           active -> past due
           active -> cancelled
           past due -> active
           past due -> cancelled"""
           
        cursor.execute("""
                        select subscription_id from subscriptions
                        where plan_id=:1 and customer_id= :2""",
                        [status_record.plan_id, customer_id],)
                        
        
        sub_result = cursor.fetchone()
        
        if sub_result is not None:
            subscription_id = sub_result[0] 
            
            cursor.execute("""
                            select status from subscriptions
                            where subscription_id=:1""",
                            [subscription_id],)
            current_status = cursor.fetchone()[0].lower() 
            
            
            mydict = {
                "trial": ["active", "cancelled"],
                "active": ["past due", "cancelled"],
                "past due": ["active", "cancelled"]
            }
            
            if current_status not in mydict:
                    raise HTTPException(status_code=401, detail="Updatable status Not Found Please choose a Valid Status")
            elif status_record.status.lower() not in mydict[current_status]:
                    raise HTTPException(status_code=401, detail="Invalid Status Updation")
            else:
                ## UPDATING/CREATING THE BILLING_CYCLES RECORD ##
                ## IF UPDATING STATUS IS ACTIVE THEN UPDATE THE CURRENT BILLING_CYCLE RECORD WITH completed and CREATE A NEW RECORD IN BILLING_CYCLE RECORD WITH PENDING STATUS
                ##FROM ANY STATUS TO CANCELLED UPDATE THE CURRENT EXISTING RECORD WITH CANCELLED
                ##FROM ACTIVE STATUS TO PAST DUE STATUS THEN CHANGE THE EXISTING RECORD WITH COMPLETED STATUS
                if status_record.status.lower() == "active":
                    cursor.execute("""
                                    select billing_interval from plans where id=:1""", [status_record.plan_id],)
                    billing_interval = cursor.fetchone()[0]
                    
                    if billing_interval.lower() == 'monthly':
                        days = 30
                    else:
                        days = 365   
                    cursor.execute(""" update billing_cycles set status=:1, updated_at=:2 where subscription_id=:3 and status=:4""",
                                   ['completed',datetime.now(),subscription_id,'pending'],)
                    cursor.execute("""
                        insert into billing_cycles
                        (subscription_id, cycle_start_date, cycle_end_date, renewal_date, status, created_at, updated_at)
                        values(:1,:2,:3,:4,:5,:6,:7)""",
                        [subscription_id,datetime.now(),datetime.now() + timedelta(days=days),datetime.now(),"pending",datetime.now(),datetime.now()],)
                    #UPDATING THE SUBSCRIPTIONS TABLE ##              
                    cursor.execute("""
                                    update subscriptions
                                    set status=:1,
                                    start_date=:2,
                                    end_date=:3
                                    where subscription_id=:4""",
                                    ["active", datetime.now(), datetime.now() + timedelta(days=days), subscription_id],)
                    ## RECORDING THE AUDIT_LOG ####
                    cursor.execute(""" 
                        insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                        values(:1,:2,:3,:4,:5,:6,:7)""",
                        ['Subscription Activated',subscription_id,'subscription Activated','',json.dumps({'customer_id': customer_id}),'user',datetime.now()],)      
                else:
                    ##this logic handles both billing_cycles and audit_logs tables ###
                    if status_record.status.lower()=='cancelled':
                        cursor.execute(""" update billing_cycles set status=:1 and updated_at=:2 where subscription_id=:3 and status=:4""",
                                        ['cancelled',datetime.now(),subscription_id,'pending'],)
                        ## RECORDING THE AUDIT_LOG ####
                        cursor.execute(""" 
                            insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                            values(:1,:2,:3,:4,:5,:6,:7)""",
                            ['Subscription cancelled',subscription_id,'subscription cancelled','',json.dumps({'customer_id': customer_id}),'user',datetime.now()],)
                    elif current_status=='active' and status_record.status.lower()=='past due':
                        cursor.execute(""" update billing_cycles set status=:1 and updated_at=:2 where subscription_id=:3 and status=:4""",
                                    ['completed',datetime.now(),subscription_id,'pending'],)
                    cursor.execute("""
                                update subscriptions 
                                set status=:1
                                where subscription_id=:2""",
                                [status_record.status.lower(),subscription_id],)  
                                
                cursor.execute("""
                                update subscriptions 
                                set updated_at=:1
                                where subscription_id=:2""",
                                [datetime.now(), subscription_id],) 
                connection.commit()
                return {"message": "Status updated successfully"}
        else:
            ### 1-CASE WHERE NEW SUBSCRIPTION RECORD IS CREATING #############
            if status_record.status.lower() =="active" or status_record.status.lower()=="trial":
                cursor.execute("""select trial_days, billing_interval from plans where id=:1""", [status_record.plan_id],)
                plan_result = cursor.fetchone()
                if plan_result is None:
                    raise HTTPException(status_code=404, detail="Plan not found")              
                trial_days = plan_result[0]
                if plan_result[1].lower()=="monthly":
                    days=30
                else:
                    days=365
                random_number = random.randint(100000, 999999)
                sub_id = f"SUB-{random_number}"         
                if trial_days > 0:
                    cursor.execute(""" INSERT INTO subscriptions
                                (subscription_id, customer_id, plan_id, status, start_date, end_date, created_at, updated_at) 
                                VALUES (:1, :2, :3, :4, :5, :6, :7, :8)""",
                                [
                                   sub_id,
                                   customer_id,
                                   status_record.plan_id,
                                   "trial",
                                   datetime.now(),
                                   datetime.now() + timedelta(days=trial_days),
                                   datetime.now(),
                                   datetime.now()
                                ],)
                    ## RECORDING THE AUDIT_LOG ####
                    cursor.execute(""" 
                        insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                        values(:1,:2,:3,:4,:5,:6,:7)""",
                        ['Subscription created',sub_id,'New subscription created with trial phase','',json.dumps({'customer_id': customer_id}),'user',datetime.now()],)
                else:
                    cursor.execute(""" INSERT INTO subscriptions
                                (subscription_id, customer_id, plan_id, status, start_date, end_date, created_at, updated_at) 
                                VALUES (:1, :2, :3, :4, :5, :6, :7, :8)""",
                                [
                                    sub_id,
                                    customer_id,
                                    status_record.plan_id,
                                    "active",
                                    datetime.now(),
                                    datetime.now() + timedelta(days=days), # Fix: Added +30 days since trial=0
                                    datetime.now(),
                                    datetime.now()
                                ],)
                    ## RECORDING THE AUDIT_LOG ####
                    cursor.execute(""" 
                        insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                        values(:1,:2,:3,:4,:5,:6,:7)""",
                        ['Subscription created',sub_id,'New subscription created with active phase','',json.dumps({'customer_id': customer_id}),'user',datetime.now()],)
                #### CREATING THE NEW BILLING_CYCLE RECORD #######################
                cursor.execute("""
                                insert into billing_cycles
                                (subscription_id, cycle_start_date, cycle_end_date, renewal_date, status, created_at, updated_at)
                                values(:1,:2,:3,:4,:5,:6,:7)""",
                                [sub_id,datetime.now(),datetime.now() + timedelta(days=days),datetime.now(),"pending",datetime.now(),datetime.now()],)
                # creating the invoice record and calculating the tax amount
                cursor.execute("""select price from plans where id=:1""",[status_record.plan_id])
                sub_total=cursor.fetchone()[0]
                tax_amount=sub_total*0.10
                total_amount=sub_total+tax_amount
                rand_num= random.randint(100000, 999999)
                invoice_id = f"INV-{rand_num}" 
                cursor.execute("""
                                insert into invoice
                                (invoice_id,subscription_id, customer_id,invoice_date,due_date,sub_total,tax_amount,total_amount,status)
                                values(:1,:2,:3,:4,:5,:6,:7,:8,:9)""",
                                [invoice_id,sub_id,customer_id,datetime.now(),datetime.now(),sub_total,tax_amount,total_amount,'paid'],)
                connection.commit()
                return {"message": "New subscription created successfully"}
            else:
                raise HTTPException(status_code=401, detail="Updatable status Is Invalid")
    finally:
        cursor.close()
        connection.close()



