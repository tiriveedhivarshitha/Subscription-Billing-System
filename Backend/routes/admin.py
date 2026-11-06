from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydanticModel import  planRecord, PlanUpdate, customerDetails
from database.oracleDBconnection import get_connection, get_admin_key, get_secret_key
from pydantic import BaseModel
import json
from datetime import datetime, timedelta
import jwt
import random



admin_router = APIRouter()

############# PLAN API'S IN ADMIN PORTAL ################

"""GET PLANS API END POINT"""
@admin_router.get("/plans")
def get_plans():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""SELECT id, name, price, billing_interval, trial_days, features
                            FROM plans where status=:1""",
                            ['active'],)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            features_raw = row[5]
            features = None
            if features_raw is not None:
                # If it's a CLOB object, read it as string
                if hasattr(features_raw, "read"):
                    features_raw = features_raw.read()
                # Parse JSON string to Python dict
                features = json.loads(features_raw)
            result.append({
                "id": row[0],
                "name": row[1],
                "price": row[2],
                "billing_interval": row[3],
                "trial_days": row[4],
                "features": features
            })
        return result
    finally:
        cursor.close()
        connection.close()


"""POSTING PLANS"""
@admin_router.post("/plans")
def post_plans(plan_record: planRecord):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        features_json = json.dumps(plan_record.features)
        random_number=random.randint(100000,999999)
        new_id=f"PLAN-{random_number}"
        cursor.execute(""" INSERT INTO plans ( id, name,price, billing_interval, trial_days, features, created_at, updated_at,status) 
                           VALUES (:1,:2, :3, :4, :5, :6,:7,:8,:9)""",
                            [
                                new_id,
                                plan_record.name,
                                plan_record.price,
                                plan_record.billing_interval,
                                plan_record.trial_days,
                                features_json,
                                datetime.now(),
                                datetime.now(),
                                plan_record.status.lower()
                            ],
                            )
        ## RECORDING THE AUDIT_LOG ####
        cursor.execute(""" 
            insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
            values(:1,:2,:3,:4,:5,:6,:7)""",
            ['plan',new_id,'plan_created','',json.dumps({'plan_name': plan_record.name}),'admin',datetime.now()],)
        connection.commit()
        return "inserted successfully"
    finally: 
        cursor.close()
        connection.close()

"""Fetching all the archived plans — FIX: route had missing slash, status was 'archieved' but archive sets 'inactive'"""
@admin_router.get("/plans/archived")
def fetch_all_archived_plans():
    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute("""SELECT id, name, price, billing_interval, trial_days, features
                                    FROM plans where status=:1""",
                                    ['inactive'],)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            features_raw = row[5]
            features = None
            if features_raw is not None:
                if hasattr(features_raw, "read"):
                    features_raw = features_raw.read()
                features = json.loads(features_raw)
            result.append({
                "id": row[0],
                "name": row[1],
                "price": row[2],
                "billing_interval": row[3],
                "trial_days": row[4],
                "features": features
                })
        return result
    finally:
        cursor.close()
        connection.close()

"""Activating A plan"""
@admin_router.put("/plan/{plan_id}")
def activate_plan(plan_id:str):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute("""select id from plans where id=:1""",[plan_id])
        record=cursor.fetchone()
        if record==None:
            raise HTTPException(status_code=404, detail="Plan not found")
        else:
            cursor.execute("""
                    update plans
                    set status=:1
                    where id=:2""",
                    ['active',plan_id])
            connection.commit()
            return {"status": "Plan activated successfully"}
    finally:
        cursor.close()
        connection.close()

""" UPDATING THE PLAN BY ID """
@admin_router.patch("/plan/{planID}")
def update_plan_by(planID:str, plan_update:PlanUpdate):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        data = plan_update.model_dump(exclude_unset=True)
        for key, value in data.items():
            cursor.execute(
                f"""
                UPDATE plans
                SET {key} = :1
                WHERE id = :2
                """,
                [value, planID]
            )
        cursor.execute(""" update plans 
                           set updated_at= :1
                           where id= :2""",
                           [datetime.now(),planID], 
                       )
        ## RECORDING THE AUDIT_LOG ####
        cursor.execute(""" 
            insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
            values(:1,:2,:3,:4,:5,:6,:7)""",
            ['plan',planID,'plan_updated','',json.dumps({'plan_updation': "Some plan features are updated"}),'admin',datetime.now()],)
        connection.commit()
        return {"message": "Plan updated successfully"}
    finally:
        cursor.close()
        connection.close()

""" Archive Plan """
@admin_router.put("/plans/archieve/{id}")
def archieving_plan(id:str):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute(""" select id from plans where id=:1""",[id],)
        is_exist=cursor.fetchone()
        if is_exist is None:
            raise HTTPException(status_code=404, detail="Plan not found")
        else:
            cursor.execute(""" update plans 
                               set status=:1
                               where id=:2""",
                               ['inactive',id],)
            ## RECORDING THE AUDIT_LOG ####
            cursor.execute(""" 
                insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                values(:1,:2,:3,:4,:5,:6,:7)""",
                ['plan',id,'Plan_archived','',json.dumps({'plan_archive': "Plan is archived"}),'admin',datetime.now()],)
            connection.commit()
            return {"Message": "Plan archived Successfully"}
    finally:
        cursor.close()
        connection.close()


####################################### CUSTOMER API'S IN ADMIN PORTAL ############################

@admin_router.get("/customers")
def get_customers():
    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute("select customer_id, name, email, created_at,updated_at from customers where role_type='user'")
        rows=cursor.fetchall()
        result=[]
        for row in rows:
                result.append({
                        "customer_id":row[0],
                        "name":row[1],
                        "email": row[2],
                        "created_at" : row[3],
                        "updated_at" : row[4]                    
        }) 
        return result
    finally:
        cursor.close()
        connection.close()

#Fetching customer based on Customer_id
@admin_router.get("/customers/{ID}")
def get_customers_by_id(ID:str):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute("select *from customers where customer_id= :1",
                       [ID])
        rows=cursor.fetchall()
        result=[]
        for row in rows:
            result.append({
                            "customer_id":row[0],
                            "name":row[1],
                            "email": row[2],
                            "created_at" : row[3],
                            "updated_at" : row[4],
                            "password" :row[5]
                    })
        return result
    finally:
        cursor.close()
        connection.close()



########################## MILESTONE 3: AUDIT LOGS & HISTORY ##################
@admin_router.get("/audit-logs")
def get_audit_logs():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT entity_type, entity_id, action, performed_by, created_at FROM audit_logs ORDER BY created_at DESC")
        records = cursor.fetchall()[:100]
        return [{"entity_type": r[0], "entity_id": r[1], "action": r[2], "user": r[3], "date": r[4]} for r in records]
    finally:
        cursor.close()
        connection.close()



####################################### MILESTONE 3: FAILED PAYMENTS & INVOICES ############################
@admin_router.get("/payments/failed")
def get_failed_payments():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT invoice_id, payment_reference,amount, payment_method,payment_date FROM payment WHERE status = 'failed'")
        records = cursor.fetchall()
        return [{"invoice_id": r[0], "payment_reference": r[1], "amount": r[2], "payment_method": r[3],"payment_date":r[4]} for r in records]
    finally:
        cursor.close()
        connection.close()

