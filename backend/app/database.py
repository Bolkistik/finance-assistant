#Файл подключения к БД
import os #Для работы с переменным окружением
from sqlalchemy import create_engine #Создает движок подключения к БД
from sqlalchemy.ext.declarative import declarative_base #базовый класс для таблиц
from sqlalchemy.orm import sessionmaker #фабрика сессий для работы с БД
from dotenv import load_dotenv #загружает переменные из .env файла

load_dotenv()

#Для локальной разработки будем использовать SQLite
#А на сервере — PostgreSQL через переменную окружения
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance.db")

#Для SQLite нужны особые настройки
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}#Снимаем ограничение для количества сессий SQLite на этапе разработки
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
#Создание фабрики сессий. autocommit - авто-сохранение изменений, autoflush - авто-отправказапросов БД, bind - привязываем к нашему движку.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Функция для получения сессии БД (будем использовать в API)
def get_db():
    db = SessionLocal() # создаем новую сессию
    try:
        yield db #отдаем сессию в обработку
    finally: #Гарантированно выполняется после завершения работы с сессией
        db.close()

#Мы гарантируем, что для каждого запроса будет создана своя сессия, а так же она будет завершена после обработки или ошибки.
#Можно легко переключиться с SQLite на PostgreSQL
#Пароли к БД хранятся в .env а не в коде
