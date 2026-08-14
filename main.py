from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
# Подключите ваши модули работы с базой данных (psycopg2 / SQLAlchemy)

app = FastAPI()

API_KEY = "my-secret-key-123"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key

# 1. Запрос на получение всех пользователей (GET /users)
@app.get("/users", status_code=200)
async def get_users():
    # Здесь должен быть SQL-запрос SELECT * FROM users;
    # Возвращает массив пользователей: [{"id": 1, "name": "..."}, ...]
    return users_list_from_db

# 2. Запрос на создание пользователя (POST /users) с защитой API Key
@app.post("/users", status_code=201, dependencies=[Security(verify_api_key)])
async def create_user(user: dict):
    # Здесь должен быть SQL-запрос INSERT INTO users ... RETURNING id, name, email, created_at;
    # Важно: возврат должен содержать созданный ID из базы!
    return created_user_with_id_from_db