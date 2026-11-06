from fastapi import APIRouter, HTTPException
from database.oracleDBconnection import get_connection, get_admin_key,get_secret_key, get_algorithm
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydanticModel import  signinRecord, signupRecord
import json
import jwt
import random
from datetime import datetime, timedelta

auth_router = APIRouter()

SECRET_KEY=get_secret_key()
ALGORITHM=get_algorithm()
############################################### SIGNIN API ################################################
@auth_router.post("/signin")
def login(signin_details:signinRecord):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        if signin_details.role_type.lower()=='admin':
            cursor.execute(""" select customer_id from customers where email=:1 and password= :2 and role_type=:3""",
                        [signin_details.Email,signin_details.Password,'admin'],
                        )
            user=cursor.fetchone()
            if user is None:
                raise HTTPException(status_code=401, detail="Invalid credentials with admin login")
            else:
                customer_id=user[0]
                token_data = {"mail": signin_details.Email, "customer_id": customer_id,"role":'admin'}
                token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)                       
                token_str = token.decode("utf-8") if isinstance(token, bytes) else token
                ## CREATING A AUDIT_LOG ########
                cursor.execute(""" 
                insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                                values(:1,:2,:3,:4,:5,:6,:7)""",
                                ['customer loggedin',customer_id,'user sign in','',json.dumps({'email': signin_details.Email}),'user',datetime.now()],)
                connection.commit()
                return {"token": token_str}
        else:
            cursor.execute(""" select customer_id from customers where email=:1 and password= :2 and role_type= :3""",
                                    [signin_details.Email,signin_details.Password,'user'],
                                    )
            user=cursor.fetchone()
            if user is None:
                raise HTTPException(status_code=401, detail="Invalid credentials with user login")
            else:
                customer_id=user[0]
                token_data = {"mail": signin_details.Email, "customer_id": customer_id,"role":'user'}
                token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)                       
                token_str = token.decode("utf-8") if isinstance(token, bytes) else token
                ## CREATING A AUDIT_LOG ########
                cursor.execute(""" 
                    insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                    values(:1,:2,:3,:4,:5,:6,:7)""",
                    ['customer loggedin',customer_id,'user sign in','',json.dumps({'email': signin_details.Email}),'user',datetime.now()],)
                connection.commit()
                return {"token": token_str}
    finally:
        cursor.close()
        connection.close()
############################################# SIGNUP API ##########################################################
@auth_router.post("/signup")
def signup(signup_details:signupRecord):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        if signup_details.role_type.lower()=='admin':
            admin=get_admin_key()
            if signup_details.secret_key==admin:
                cursor.execute(""" select customer_id from customers where email=:1 """,
                                       [signup_details.Email],
                                       )
                if cursor.fetchone() is not None:
                    raise HTTPException(status_code=400, detail="Admin already exists. Please login.")
                else:
                    random_number=random.randint(100000,999999)
                    customer_id=f"CUST-{random_number}"
                    cursor.execute("""
                                insert into customers(customer_id, name, email, created_at, updated_at, password,role_type) 
                                values(:1,:2, :3,:4,:5,:6,:7)""",
                                [customer_id,signup_details.Name, signup_details.Email, datetime.now(),datetime.now(),signup_details.Password,'admin'],
                            )
                    ## RECORDING THE AUDIT_LOG ####
                    cursor.execute(""" 
                                insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                                values(:1,:2,:3,:4,:5,:6,:7)""",
                                ['Admin Created',customer_id,'user sign up','',json.dumps({'email': signup_details.Email}),'user',datetime.now()],)
                    connection.commit() 
                    return {"message": "Account created. Please login now!"}   
            else:
                raise HTTPException(status_code=400, detail="Invalid Admin Key") 
        else:
            cursor.execute(""" select customer_id from customers where email=:1 """,
                       [signup_details.Email],
                       )
            if cursor.fetchone() is not None:
                raise HTTPException(status_code=400, detail="User already exists. Please login.")
            else:
                random_number=random.randint(100000,999999)
                customer_id=f"CUST-{random_number}"
                cursor.execute("""
                            insert into customers(customer_id, name, email, created_at, updated_at, password,role_type) 
                            values(:1,:2, :3,:4,:5,:6,:7)""",
                            [customer_id,signup_details.Name, signup_details.Email, datetime.now(),datetime.now(),signup_details.Password,'user'],
                            )
                ## RECORDING THE AUDIT_LOG ####
                cursor.execute(""" 
                            insert into audit_logs(entity_type,entity_id,action,old_value, new_value,performed_by,created_at)
                            values(:1,:2,:3,:4,:5,:6,:7)""",
                            ['customer created',customer_id,'user sign up','',json.dumps({'email': signup_details.Email}),'user',datetime.now()],)
            connection.commit() 
            return {"message": "Account created. Please login now!"}
    finally:
        cursor.close()
        connection.close()
