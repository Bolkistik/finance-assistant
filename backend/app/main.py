from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List

from . import models, schemas
from .database import engine, get_db

#Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Assistant API") #Создаем приложение с названием "title"

#Настройка CORS для работы React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://fass.gotoknow.ru"],
    allow_credentials=True, # Разрешаем отправку cookies
    allow_methods=["*"], # Разрешаем все HTTP методы
    allow_headers=["*"], # Разрешаем все заголовки
)

@app.get("/") #Декоратор @app говорит, что функция root вызывается при GET запросе
def root():
    return {"message": "Finance Assistant API работает!"} #Возвращает словарь {message}

@app.get("/health")
def health(): #Создает эндпоинт для проверки системы 
    return {"status": "ok"}

#Минимально рабочая версия - эндпойнты

@app.get("/api/balance/{target_date}")
def get_balance(target_date: date, db: Session = Depends(get_db)):
    # Получение накопленного баланса на указанную дату
    accumulated = db.query(models.AccumulatedDaily).filter(
        models.AccumulatedDaily.date == target_date
    ).first()

    if accumulated:
        return {"date": target_date, "balance": accumulated.end_of_day_balance}
    
    # Если записи нет, считаем баланс вручную
    from sqlalchemy import func

    total = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.date <=target_date,
        models.Transaction.transaction_type == "actual"
    ).scalar() or 0

    return {"date": target_date, "balance": total}

# Работа с транзакциями
@app.get("/api/transactions")
def get_transactions(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    #ПОлучение транзакций за период
    transactions = db.query(models.Transaction).filter(
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
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
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
        {"name": "Продукты", "type": "expence", "is_accumulative": True, "color": "#ff9800"},
        {"name": "Авто", "type": "expence", "is_accumulative": True, "color": "#2196f3"},
        {"name": "Прочее", "type": "expence", "is_accumulative": True, "color": "#9c27b0"},
        {"name": "Рестораны", "type": "expence", "is_accumulative": False, "color": "#f44336"},
    ]

    for cat_data in default_categories:
        exiting = db.query(models.category).filter_by(name=cat_data["name"]).first()
        if not exiting:
            category = models.Category(**cat_data)
            db.add(category)

    db.commit()
    return {"message": "Categories initialized"}