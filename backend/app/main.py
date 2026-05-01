from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List

from . import models, schemas
from .database import engine, Base, get_db

#Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Assistant API") #Создаем приложение с названием "title"

#Настройка CORS для работы React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://fass.gotoknow.ru"],
    allow_credentials=True, # Разрешаем отправку cookies
    allow_methods=["*"], # Разрешаем все HTTP методы
    allow_headers=["*"], # Разрешаем все заголовки
)

#Автоинициализация БД
def init_db():
    #Создает базовые категории если их нет.
    db = next(get_db())
    try:
        existing = db.query(models.Category).first()
        if not existing:
            default_categories = [
                {"name": "Зарплата", "type": "income", "is_accumulative": False, "color": "#4caf50"},
                {"name": "Продукты", "type": "expense", "is_accumulative": True, "color": "#ff9800"},
                {"name": "Авто", "type": "expense", "is_accumulative": True, "color": "#2196f3"},
                {"name": "Прочее", "type": "expense", "is_accumulative": True, "color": "#9c27b0"},
                {"name": "Рестораны", "type": "expense", "is_accumulative": True, "color": "#f44336"},
            ]
            for cat_data in default_categories:
                category = models.Category(**cat_data)
                db.add(category)
            db.commit()
            print("Категории инициализированы!")
    finally:
        db.close()

init_db()

@app.get("/") #Декоратор @app говорит, что функция root вызывается при GET запросе
def root():
    return {"message": "Finance Assistant API работает!"} #Возвращает словарь {message}

@app.get("/health")
def health(): #Создает эндпоинт для проверки системы 
    return {"status": "ok"}

#Минимально рабочая версия - эндпойнты

@app.get("/api/balance/{target_date}")
def get_balance(target_date: date, db: Session = Depends(get_db)):
    from sqlalchemy import func

    #Доходы
    income = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.date <= target_date,
        models.Transaction.transaction_type == "actual",
        models.Transaction.amount > 0
    ).scalar() or 0

    #Расходы
    expense = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.date <= target_date,
        models.Transaction.transaction_type == "actual",
        models.Transaction.amount < 0
    ).scalar() or 0

    balance = income + expense

    return {
        "date": target_date,
        "balance": round(balance, 2),
        "income": round(income, 2),
        "expense": round(abs(expense), 2)
    }

# Работа с транзакциями
@app.get("/api/transactions")
def get_transactions(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    #ПОлучение транзакций за период
    from sqlalchemy.orm import joinedload
    transactions = db.query(models.Transaction)\
        .options(joinedload(models.Transaction.category_ref))\
        .filter(
        models.Transaction.date >= start_date,
        models.Transaction.date <= end_date
    ).order_by(models.Transaction.date.desc()).all()

    return transactions
@app.post("/api/transactions")
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db)
):
    #Создание новой транзакции
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    db.refresh(db_transaction, attribute_names=['category_ref'])
    return db_transaction

@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    #Получение списка категорий
    categories = db.query(models.Category).all()
    return categories

@app.post("/api/categories/init")
def init_default_categories(db: Session = Depends(get_db)):
    #Инициализация базовых категорий
    default_categories = [
        {"name": "Зарплата", "type": "income", "is_accumulative": False, "color": "#4caf50"},
        {"name": "Продукты", "type": "expense", "is_accumulative": True, "color": "#ff9800"},
        {"name": "Авто", "type": "expense", "is_accumulative": True, "color": "#2196f3"},
        {"name": "Прочее", "type": "expense", "is_accumulative": True, "color": "#9c27b0"},
        {"name": "Рестораны", "type": "expense", "is_accumulative": False, "color": "#f44336"},
    ]

    for cat_data in default_categories:
        existing = db.query(models.Category).filter_by(name=cat_data["name"]).first()
        if not existing:
            category = models.Category(**cat_data)
            db.add(category)

    db.commit()
    return {"message": "Categories initialized"}