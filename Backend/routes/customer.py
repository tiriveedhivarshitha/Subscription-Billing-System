from fastapi import APIRouter, FastAPI,Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydanticModel import products, planRecord, CustomerRecord, PlanUpdate, subscriptionValidation, customerDetails, PaymentRequest,WebhookPayload
from database.oracleDBconnection import get_connection, get_admin_key, get_secret_key
from dependencies import get_current_customer
import json
from datetime import datetime, timedelta
import random
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.responses import FileResponse


customer_router = APIRouter()

################################################################ PLANS API'S ####################################################
"""GET PLANS API END POINT"""
@customer_router.get("/plans")
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
                "plan_id": row[0],
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

"""GETTING THE PLAN BY NAME"""
@customer_router.get("/plans/{plan_name}")
def get_plan_by_name(plan_name: str):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute(
                    """SELECT id, name, price, billing_interval, trial_days, features
                    FROM plans where UPPER(name)= UPPER(:1) and status=:2""",
                    [plan_name,'active'],
        )
        rows=cursor.fetchall()
        if rows==None:
            raise HTTPException(status_code=404, detail="Plan not found")
        result=[]
        for row in rows:
            features_raw = row[5]
            features = None
            if features_raw is not None:
                # If it's a LOB object, read it as string
                if hasattr(features_raw, "read"):
                    features_raw = features_raw.read()
                # Parse JSON string to Python dict
                features = json.loads(features_raw)
            result.append({
                            "plan_id": row[0],
                            "name": row[1],
                            "price": row[2],
                            "billing_interval": row[3],
                            "trial_days": row[4],
                            "features": features,
                        })
        return result

    finally:
        cursor.close()
        connection.close()

####################################### (SUBSCRIPTION AND MOCK PAYMENT) ############################


@customer_router.post("/payments/process")
def process_payment(payment: PaymentRequest,customer_id: str =Depends(get_current_customer)):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        is_success = random.random() < 0.8
        cursor.execute("""select price, billing_interval from plans where id =:1""",[payment.plan_id])
        row=cursor.fetchone()
        subtotal=row[0]
        total_days=row[1]
        transaction_id = f"TXN-{random.randint(100000, 999999)}"
        if is_success:
            ######### CRETING A SUBSCRIPTION RECORD ######
            days=0
            if total_days=='Mobile Monthly' or total_days=='Basic Monthly' or total_days=='standard Monthly' or total_days=='Premium Monthly':
                days=30
            else:
                days=30
            subscription_id=f"SUB-{random.randint(100000, 999999)}"
            cursor.execute("""insert into subscriptions(subscription_id,customer_id,plan_id,status,start_date,end_date,created_at,updated_at)
                        values(:1,:2,:3,:4,:5,:6,:7,:8)""",
                        [subscription_id,customer_id,payment.plan_id,'active',datetime.now(),datetime.now()+timedelta(days),datetime.now(),datetime.now()])
            ##########CREATING A INVOICE RECORD###########
            invoice_id=f"INV-{random.randint(100000, 999999)}"
            tax_amount=(0.18)*(subtotal)
            total_amount=subtotal+tax_amount
            cursor.execute("""insert into invoice(invoice_id,subscription_id,customer_id,invoice_date,subtotal,tax_amount,total_amount, status)
                        values(:1,:2,:3,:4,:5,:6,:7,:8)""",
                        [invoice_id,subscription_id,customer_id,datetime.now(),subtotal,tax_amount,total_amount,'paid'])
            ########creating a payment record ######
            cursor.execute("""insert into payment(invoice_id,payment_reference,amount,payment_method,status,payment_date)
                        values(:1,:2,:3,:4,:5,:6)""",
                        [invoice_id,transaction_id,subtotal,payment.payment_method,"success",datetime.now()])
            ######## creating a audit log #########
            cursor.execute("""
                        INSERT INTO audit_logs(entity_type, entity_id, action, old_value, new_value, performed_by, created_at)
                        VALUES (:1,:2, :3, :4,:5,:6,:7)""",
                     ["subscription",subscription_id, "subscription_created",None,None, customer_id, datetime.now()])
            connection.commit()
            return {"status": "success", "transaction_id": transaction_id, "event": "payment_success"}
        else:
            cursor.execute("""insert into payment(invoice_id,payment_reference,amount,payment_method,status,payment_date)
                                    values(:1,:2,:3,:4,:5,:6)""",
                                    [None,transaction_id,subtotal,payment.payment_method,"failed",datetime.now()])
            cursor.execute("""
                            INSERT INTO audit_logs(entity_type, entity_id, action, old_value, new_value, performed_by, created_at)
                            VALUES (:1,:2, :3, :4,:5,:6,:7)""",
                            ["subscription",payment.plan_id, "payment_failed",None,None, customer_id, datetime.now()])
            connection.commit()
            return {"status": "failed", "transaction_id": transaction_id, "event": "payment_failed",
                    "reason": "There is an Error while processing your payment-Please try after sometime"}
    finally:
        cursor.close()
        connection.close()

#############  Trial Days API ###############
@customer_router.post("/subscriptions/trial")
def take_free_trial(payment: PaymentRequest, customer_id: str = Depends(get_current_customer)):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""SELECT trial_days FROM plans WHERE id = :1""", [payment.plan_id])
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Plan not found")
        trial_days = row[0]
        subscription_id = f"SUB-{random.randint(100000, 999999)}"
        start_date = datetime.now()
        end_date = start_date + timedelta(days=trial_days)
        cursor.execute("""
            INSERT INTO subscriptions(subscription_id, customer_id, plan_id, start_date, end_date, status, created_at, updated_at)
            VALUES(:1, :2, :3, :4, :5, :6, :7, :8)
        """, [subscription_id, customer_id, payment.plan_id, start_date, end_date, 'trial', datetime.now(), datetime.now()])

        cursor.execute("""
            INSERT INTO audit_logs(entity_type, entity_id, action, old_value, new_value, performed_by, created_at)
            VALUES(:1, :2, :3, :4, :5, :6, :7)
        """, ["subscription", subscription_id, "trial_started", None, None, customer_id, datetime.now()])

        connection.commit()
        return {"status": "trial_started", "subscription_id": subscription_id, "trial_ends": end_date}
    finally:
        cursor.close()
        connection.close()


####################################### TASK-1(INVOICE GENERATION) ############################

""" get all invoices """
@customer_router.get("/invoices")
def get_all_invoices(customer_id: str = Depends(get_current_customer)):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute("""select *from invoice where customer_id=:1""",[customer_id])
        records=cursor.fetchall()
        if not records:
            raise HTTPException(status_code=404, detail="Customer doesn't have any invoices")
        record_list=[]
        for record in records:
            record_list.append(
                {
                    "invoice_id": record[0],
                    "subscription_no": record[1],
                    "customer_id":record[2],
                    "invoice_date":record[3],
                    "sub_total":record[4],
                    "tax_amount":record[5],
                    "total_amount":record[6],
                    "status":record[7]
                }
            )
        return record_list
    finally:
        cursor.close()
        connection.close()

""" invoice download"""
@customer_router.get("/invoices/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: str):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT invoice_id, subscription_id, customer_id, invoice_date, subtotal, tax_amount, total_amount, status FROM invoice WHERE invoice_id = :1", [invoice_id])
        record = cursor.fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="Invoice not found")

        pdf_file = f"{invoice_id}.pdf"
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(pdf_file)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(100, 800, "INVOICE RECEIPT")

        c.setFont("Helvetica", 12)
        c.drawString(100, 750, f"Invoice ID: {record[0]}")
        c.drawString(100, 730, f"Customer: {record[2]}")
        c.drawString(100, 710, f"Date: {record[3].strftime('%Y-%m-%d')}")
        c.drawString(100, 690, f"Subscription ID: {record[1]}")
        c.drawString(100, 670, f"Status: {record[7].upper()}")
        c.drawString(100, 630, f"Subtotal: Rs. {record[4]}")
        c.drawString(100, 610, f"Tax Amount: Rs. {record[5]}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 580, f"TOTAL DUE: Rs. {record[6]}")

        c.save()
        return FileResponse(path=pdf_file, filename=f"Invoice_{invoice_id}.pdf", media_type='application/pdf')
    finally:
        cursor.close()
        connection.close()

""" get invoice by id"""
@customer_router.get("/invoices/{invoice_id}")
def get_invoice_by_id(invoice_id:str):
    connection=get_connection()
    cursor=connection.cursor()
    try:
        cursor.execute("""select *from invoice where invoice_id=:1""",[invoice_id])
        record=cursor.fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="Invalid InvoiceID")
        record_list=[]
        record_list.append(
                {
                    "invoice_id": record[0],
                    "subscription_no": record[1],
                    "customer_id":record[2],
                    "invoice_date":record[3],
                    "sub_total":record[4],
                    "tax_amount":record[5],
                    "total_amount":record[6],
                    "status":record[7]
                }
            )
        return record_list
    finally:
        cursor.close()
        connection.close()

############ Paid Invoices Api #############
@customer_router.get("/my-paid-invoices")
def get_my_paid_invoices(customer_id: str = Depends(get_current_customer)):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT invoice_id, total_amount, invoice_date FROM invoice WHERE customer_id = :1 AND status = 'paid'", [customer_id])
        records = cursor.fetchall()
        return [{"invoice_id": r[0], "amount": r[1], "invoice_date": r[2]} for r in records]
    finally:
        cursor.close()
        connection.close()

########### Active subscription API #########
@customer_router.get("/my-active-subscriptions")
def get_my_active_subscriptions(customer_id: str =Depends(get_current_customer)):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT subscription_id, plan_id, end_date, status FROM subscriptions WHERE customer_id = :1 AND status IN ('active', 'trial')", [customer_id])
        records = cursor.fetchall()
        return [{"subscription_id": r[0], "plan_id": r[1], "end_date": r[2], "status": r[3]} for r in records]
    finally:
        cursor.close()
        connection.close()


############################ SUBSCRIPTION STATUS AUTO-UPDATER ############################

def auto_complete_subscriptions():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT subscription_id FROM subscriptions
            WHERE end_date <= :1 AND status IN ('trial', 'active')
        """, [datetime.now()])
        expired = cursor.fetchall()
        for row in expired:
            cursor.execute("""
                UPDATE subscriptions SET status = 'completed', updated_at = :1
                WHERE subscription_id = :2
            """, [datetime.now(), row[0]])
        connection.commit()
        print(f"[Scheduler] Marked {len(expired)} subscriptions as completed.")
    finally:
        cursor.close()
        connection.close()

@customer_router.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(auto_complete_subscriptions, 'interval', minutes=1)
    scheduler.start()
    print("Scheduler started: checking subscriptions every minute")
