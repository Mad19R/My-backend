import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

app = FastAPI(title="My Analytics API Extended")

# CORS настройка
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Pydantic-модели для валидации входящих данных
class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

# --- ENDPOINTS: USERS ---

@app.get("/users", summary="Получить всех пользователей")
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, created_at FROM users ORDER BY id;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

@app.get("/users/{user_id}", summary="Получить пользователя по ID")
def get_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, created_at FROM users WHERE id = %s;", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", status_code=201, summary="Создать нового пользователя")
def create_user(user: UserCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email, created_at;",
            (user.name, user.email)
        )
        new_user = cur.fetchone()
        conn.commit()
        return new_user
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="User with this email already exists")
    finally:
        cur.close()
        conn.close()

@app.put("/users/{user_id}", summary="Обновить данные пользователя")
def update_user(user_id: int, user: UserUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users WHERE id = %s;", (user_id,))
    existing_user = cur.fetchone()
    if not existing_user:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    new_name = user.name if user.name is not None else existing_user["name"]
    new_email = user.email if user.email is not None else existing_user["email"]

    cur.execute(
        "UPDATE users SET name = %s, email = %s WHERE id = %s RETURNING id, name, email, created_at;",
        (new_name, new_email, user_id)
    )
    updated_user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return updated_user

@app.delete("/users/{user_id}", status_code=204, summary="Удалить пользователя")
def delete_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
    deleted = cur.fetchone()
    if not deleted:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.commit()
    cur.close()
    conn.close()
    return None

# --- ENDPOINTS: ORDERS & JOIN QUERIES ---

@app.get("/orders", summary="Получить список заказов с деталями (JOIN)")
def get_orders():
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        SELECT 
            o.id AS order_id,
            u.name AS user_name,
            p.title AS product_title,
            o.quantity,
            (p.price * o.quantity) AS total_price,
            o.status,
            o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        ORDER BY o.id;
    """
    cur.execute(query)
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return orders

@app.post("/orders", status_code=201, summary="Создать новый заказ")
def create_order(order: OrderCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING id, user_id, product_id, quantity, status, created_at;",
            (order.user_id, order.product_id, order.quantity)
        )
        new_order = cur.fetchone()
        conn.commit()
        return new_order
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Invalid user_id or product_id")
    finally:
        cur.close()
        conn.close()