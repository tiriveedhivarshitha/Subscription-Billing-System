from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import auth_router
from routes.admin import admin_router
from routes.customer import customer_router 

apple = FastAPI()

apple.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


apple.include_router(auth_router,     prefix="/auth")
apple.include_router(admin_router,    prefix="/admin")
apple.include_router(customer_router, prefix="/customer")






