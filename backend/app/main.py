from fastapi import FastAPI

app = FastAPI(title="Finance Assistant API") #Создаем приложение с названием "title"

@app.get("/") #Декоратор @app говорит, что функция root вызывается при GET запросе
def root():
    return {"message": "Finance Assistant API работает!"} #Возвращает словарь {message}

@app.get("/health")
def health(): #Создает эндпоинт для проверки системы 
    return {"status": "ok"}