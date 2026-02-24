#Этот файл определяет как данные передаются из БД по API
from pydantic import BaseModel
from datetime import date
from typing import Optional

#pedantic проверит, что date-дата, amount-можно преобразовать в float, category-строка
class TransactionBase(BaseModel):
    date: date #дата транзакции
    amount: float #сумма
    category: str #категория 
    description: Optional[str] = None
    is_planned: bool = False #плановая операция?
#Наследует все поля от TransactionBase. Когда клиент отправляет данные для создания новой транзакции.
class TransactionCreate(TransactionBase):
    pass
#Создает полную модель вместе с id из БД
class Transaction(TransactionBase):
    id: int

    class Config:
        from_attributes = True
#Простая модель для ответа на запрос баланса.
class BalanceResponse(BaseModel):
    date: date
    balance: float