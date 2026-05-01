#Этот файл определяет как данные передаются из БД по API
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

#pedantic проверит, что date-дата, amount-можно преобразовать в float, category-строка
class TransactionBase(BaseModel):
    date: date #дата транзакции
    amount: float #сумма
    description: Optional[str] = None
    transaction_type: str= "actual"
    is_manual: bool = True
    category_id: int
#Наследует все поля от TransactionBase. Когда клиент отправляет данные для создания новой транзакции.
class TransactionCreate(TransactionBase):
    pass
#Создает полную модель вместе с id из БД
class Transaction(TransactionBase):
    id: int
    category_ref: Optional[dict] = None

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    type: str
    is_accumulative: bool = False
    color: str = "#000000"
    icon: Optional[str]= None

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

#Простая модель для ответа на запрос баланса.
class BalanceResponse(BaseModel):
    date: date
    balance: float
    income: float = 0.0
    expense: float = 0.0