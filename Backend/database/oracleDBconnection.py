import oracledb 
import os
from dotenv import load_dotenv
# Oracle connection details
load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN")
    )
def get_admin_key():
    return os.getenv("ADMIN_SECRET_KEY")
def get_secret_key():
    return os.getenv("SECRET_KEY")
def get_algorithm():
    return os.getenv("ALGORITHM")

