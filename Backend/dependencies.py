from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database.oracleDBconnection import get_secret_key
import jwt
security = HTTPBearer()
def get_current_customer(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        SECRET_KEY = get_secret_key()
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["customer_id"]
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")
