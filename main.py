import os
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
# Если используете psycopg2/SQLAlchemy — убедитесь, что импорты на месте

app = FastAPI()

# 1. Настройка ключа авторизации
API_KEY = "my-secret-key-123"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key

# 2. Ручка GET /users (получить всех)
@app.get("/users", status_code=200)
async def get_users():
    try:
        # Твоя логика получения из базы данных:
        # users = fetch_users_from_db()
        # return users
        
        # Временная заглушка (для проверки работы сервера):
        return [
            {"id": 1, "name": "Madiyar Sumbembayev", "email": "madiyar@example.com"},
            {"id": 2, "name": "Alexey Ivanov", "email": "alexey@example.com"}
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Ручка POST /users (создать пользователя c защитой API Key)
@app.post("/users", status_code=201, dependencies=[Security(verify_api_key)])
async def create_user(user: dict):
    try:
        # Твоя логика сохранения в базу данных:
        # new_user = insert_user_to_db(user)
        # return new_user
        
        # Временная заглушка (возвращает объект с сгенерированным ID):
        return {
            "id": 99,
            "name": user.get("name", "Test User"),
            "email": user.get("email", "test@example.com")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))