CATEGORY_KEYWORDS = {
    "Продукты": ["магнит", "пятерочка", "перекресток", "ашан", "продукты", "супермаркет", "fix price"],
    "Рестораны": ["ресторан", "кафе", "шаверма", "starbucks", "mac", "kfc", "бургер", "суши", "пицца"],
    "Транспорт": ["такси", "yandex", "яндекс","аэро", "метро", "автобус", "бензин", "азс"],
    "Связь": ["мтс", "билайн", "мегафон", "tele2", "интернет", "ростелеком"],
    "Коммунальные": ["жку", "коммунальные", "электроэнергия", "вода", "газ", "отопление", "квартплата"],
    "Переводы": ["перевод", "сбп", "т-банк", "тинькофф", "сбер", "отправил", "получил"],
    "Зарплата": ["зарплата", "зп", "аванс", "оклад", "доход"],
    "Здоровье": ["аптека", "doctor", "клиника", "больница", "стоматолог", "анализы"],
    "Развлечения": ["кино", "театр", "концерт", "боулинг", "квест", "парк"],
    "Одежда": ["одежда", "обувь", "wildberries", "ozon", "lamoda"],
}

def guess_category(description: str) -> str:
    """Определяет категории по описанию транзакции"""
    if not description:
        return "Прочее"
    
    description_lower = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
            
    return "Прочее"

def determine_transaction_type(amount: float, category: str) -> str:
    """Определяет тип транзакции +/-"""
    if amount < 0:
        return "expense"
    
    income_categories = ["Зарплата", "Переводы"]
    if category in income_categories:
        return "income"
    
    return "expense"