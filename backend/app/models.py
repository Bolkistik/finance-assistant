#Этот файл для моделей таблиц
from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from .database import Base #базовый класс моделей (создан в database.py через declarative_base)

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
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_planned = Column(Boolean, default=False)