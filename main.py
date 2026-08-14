from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader

app = FastAPI()

# Define secret key and header parameter
API_KEY = "my-secret-key-123"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key

# Example protected endpoint (POST /users)
@app.post("/users", status_code=201, dependencies=[Security(verify_api_key)])
async def create_user(user: dict):
    # Твоя логика сохранения пользователя
    return user