import io
import pdfplumber
import re
from datetime import datetime
from typing import List, Dict, Any
from .category_matcher import guess_category, determine_transaction_type

def clean_amount(amount_str: str) -> float:
    """Очищает строку суммы и преобразует в число"""
    if not amount_str or amount_str.strip() == "":
        return 0.0
    
    cleaned = amount_str.replace(" ", "").replace("+", "").replace(",", ".")
    
    match = re.search(r'(\d+\.?\d*)', cleaned)
    if match:
        cleaned = match.group(1)
    
    if not cleaned:
        return 0.0
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def clean_date(date_str: str) -> datetime.date:
    """Преобразует строку даты в объект date"""
    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y").date()
    except ValueError:
        return datetime.now().date()

def is_auth_code(text: str) -> bool:
    """Проверяет, является ли строка кодом авторизации (6 цифр)"""
    return bool(re.match(r'^\d{6}$', text.strip()))

def merge_multiline_transactions(rows: List[List[str]]) -> List[List[str]]:
    """Объединяет многострочные транзакции"""
    merged = []
    i = 0
    
    while i < len(rows):
        row = rows[i]
        has_date = len(row) > 0 and row[0] and re.match(r'\d{2}\.\d{2}\.\d{4}', row[0].strip())
        
        if has_date:
            current = row.copy()
            skip_next = False
            
            if i + 1 < len(rows):
                next_row = rows[i + 1]
                if len(next_row) > 0 and (not next_row[0] or is_auth_code(next_row[0])):
                    for j in range(min(len(current), len(next_row))):
                        if next_row[j] and not current[j]:
                            current[j] = next_row[j]
                    skip_next = True
            
            merged.append(current)
            i += 2 if skip_next else 1
        else:
            i += 1
    
    return merged

def parse_sber_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    transactions = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        all_rows = []

        for page in pdf.pages:
            tables = page.extract_tables()

            if tables and len(tables) > 0 and len(tables[0]) > 0:
                for table in tables:
                    if not table:
                        continue
                    for row in table:
                        cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                        if any("ДАТА ОПЕРАЦИИ" in cell.upper() for cell in cleaned_row):
                            continue
                        if any("ИТОГО" in cell.upper() for cell in cleaned_row):
                            continue
                        if any("ОСТАТОК" in cell.upper() for cell in cleaned_row):
                            continue
                        if all(not cell for cell in cleaned_row):
                            continue
                        all_rows.append(cleaned_row)
            else:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    
                    date_match = re.search(r'^(\d{2}\.\d{2}\.\d{4})', line)
                    if not date_match:
                        continue
                    date_str = date_match.group(1)
                    rest = line[date_match.end():].strip()

                    time_match = re.search(r'^(\d{2}:\d{2})', rest)
                    if time_match:
                        rest = rest[time_match.end():].strip()

                    amount_match = re.search(r'([\+\d\s,]+\.?\d{2})(?=\s{4,})', rest)
                    if not amount_match:
                        amount_match = re.search(r'([\+\d\s,]+\.?\d{2})', rest)
                    if not amount_match:
                        continue
                    
                    amount_str = amount_match.group(1).strip()
                    
                    if is_auth_code(amount_str):
                        continue
                    
                    # Убираем сумму из rest, чтобы получить категорию
                    rest = rest[:amount_match.start()] + rest[amount_match.end():]
                    rest = rest.strip()

                    # Категория и описание
                    parts = rest.split(maxsplit=1)
                    category = parts[0] if parts else "Прочее"
                    description = parts[1] if len(parts) > 1 else ""

                    all_rows.append([date_str, "", category, amount_str, description])

        merged_rows = merge_multiline_transactions(all_rows)

        for row in merged_rows:
            if len(row) < 4:
                continue

            date_str = row[0] if len(row) > 0 else ""
            if not re.match(r'\d{2}\.\d{2}\.\d{4}', date_str):
                continue

            category = row[2] if len(row) > 2 else "Прочее"
            description = row[4] if len(row) > 4 else ""
            
            # Сумма может быть в row[3]
            amount_str = row[3] if len(row) > 3 else ""
            if not amount_str or is_auth_code(amount_str):
                continue

            try:
                date = clean_date(date_str)
                amount = clean_amount(amount_str)
                
                full_description = f"{category} | {description}" if description else category
                category_name = guess_category(full_description)
                transaction_type = determine_transaction_type(amount, category_name)
                
                if transaction_type == "expense" and amount > 0:
                    amount = -amount

                transactions.append({
                    "date": date.isoformat(),
                    "description": full_description[:200],
                    "amount": round(amount, 2),
                    "category_name": category_name,
                    "transaction_type": transaction_type
                })
            except Exception as e:
                print(f"Ошибка парсинга строки: {row}, ошибка: {e}")
                continue

    return transactions