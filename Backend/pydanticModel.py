from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
class products(BaseModel):
    id:int
    name: str
    qty: int
    price:float

class planRecord(BaseModel):
    name :str
    price:float
    billing_interval :str 
    trial_days :int
    features: Dict[str,List[str]]
    status:str

class CustomerRecord(BaseModel):
    customer_id:str
    name:str
    email:str
    created_at:datetime
    updated_at:datetime
    password:str

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    billing_interval:Optional[str]=None
    trial_days: Optional[int]=None
    created_at:Optional[datetime]=None
    updated_at:Optional[datetime]=None
    status:Optional[str]=None

class signinRecord(BaseModel):
    Email:str
    Password:str
    role_type:str

class signupRecord(BaseModel):
    Name:str
    Email:str
    Password:str
    role_type:str
    secret_key: Optional[str] = None

class subscriptionValidation(BaseModel):
    plan_id:str
    status:str

class customerDetails(BaseModel):
    name: Optional[str] = None
    email:Optional[str]=None
    password:Optional[str]=None

class PaymentRequest(BaseModel):
    plan_id :str
    payment_method:str
class WebhookPayload(BaseModel):
    event: str
    invoice_id: str