#Этот файл для моделей таблиц
from sqlalchemy import Column, Integer, String, Float, Date, Boolean, DateTime, ForeignKey, Enum, Index
from .database import Base #базовый класс моделей (создан в database.py через declarative_base)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

#Перечисления
class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    ACCUMULATIVE = "accumulative"

class TransactionType(str, enum.Enum):
    PLAN = "plan"
    ACTUAL = "actual"

#Модели
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(Enum(CategoryType), nullable=False)
    is_accumulative = Column(Boolean, default=False)
    color = Column(String, default="#000000")
    icon = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="category_ref")
    monthly_budgets = relationship("MonthlyBudget", back_populates="category_ref")

class Transaction(Base): #Класс Transaction наследуется от Base, что делает его моделью SQLAlchemy
    __tablename__ = "transactions" #если не указать __tablename__, SQLAlchemy попытается создать имя автоматически
#Integer - целочисленный тип
#primary_key=True - первичный ключ
#index=True - создать индекс для этого поля, ускоряет поиск по id
#Date - хранит только дату, для времени надо DateTime
#nullable - обязательно для заполнения

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    transaction_type = Column(Enum(TransactionType), nullable=False, default=TransactionType.ACTUAL)
    is_manual = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    category_ref = relationship("Category", back_populates="transactions")

    __table_args__ = (
        Index('ix_transactions_date_type', 'date', 'transaction_type'),
    )

class MonthlyBudget(Base):
    __tablename__ = "monthly_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String(7), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    planned_amount = Column(Float, default=0.0)
    actual_amount = Column(Float, default=0.0)
    payment_day = Column(Integer, nullable=True)
    
    category_ref = relationship("Category", back_populates="monthly_budgets")
    
    __table_args__ = (
        Index('ix_monthly_budgets_year_month', 'year_month'),
    )


class SalarySchedule(Base):
    __tablename__ = "salary_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String(7), nullable=False)
    advance_date = Column(Date, nullable=True)
    advance_amount = Column(Float, default=0.0)
    salary_date = Column(Date, nullable=True)
    salary_amount = Column(Float, default=0.0)
    advance_received = Column(Boolean, default=False)
    salary_received = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('ix_salary_schedule_year_month', 'year_month', unique=True),
    )


class Credit(Base):
    __tablename__ = "credits"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    planned_date = Column(Date, nullable=True)
    planned_amount = Column(Float, default=0.0)
    actual_date = Column(Date, nullable=True)
    actual_amount = Column(Float, default=0.0)
    is_paid = Column(Boolean, default=False)


class CreditCard(Base):
    __tablename__ = "credit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    statement_date = Column(Date, nullable=True)
    balance = Column(Float, default=0.0)
    interest_rate = Column(Float, default=0.0)
    accrued_interest = Column(Float, default=0.0)


class AccumulatedDaily(Base):
    __tablename__ = "accumulated_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True)
    products_remaining = Column(Float, default=0.0)
    auto_remaining = Column(Float, default=0.0)
    other_remaining = Column(Float, default=0.0)
    daily_limit_products = Column(Float, nullable=True)
    daily_limit_auto = Column(Float, nullable=True)
    daily_limit_other = Column(Float, nullable=True)
    end_of_day_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    __table_args__ = (
        Index('ix_accumulated_daily_date', 'date'),
    )