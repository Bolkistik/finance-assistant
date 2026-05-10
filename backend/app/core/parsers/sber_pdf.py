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
    
def merge_multiline_transactions(rows: List[List[str]]) -> List[List[str]]:
    merged = []
    i = 0

    while i < len(rows):
        row = rows[i]

        has_date = len(row) > 0 and row[0] and re.match(r'\d{2}\.\d{2}\.\d{4}', row[0].strip())
        if has_date:
            current = row.copy()
            if i+1 < len(rows):
                next_row = rows[i + 1]

                if len(next_row) > 0 and (not next_row[0] or re.match(r'\d{6}', next_row[0].strip())):
                    for j in range(min(len(current), len(next_row))):
                        if next_row[j] and not current[j]:
                            current[j] = next_row[j]
                    i += 1
            merged.append(current)
        else:
            pass
        i +=1
    return merged

def parse_sber_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    transactions = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        all_rows = []

        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue
                for row in table:
                    cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                    if any("Дата операции" in cell.upper() for cell in cleaned_row):
                        continue
                    if any("ИТОГО" in cell for cell in cleaned_row):
                        continue
                    if all(not cell for cell in cleaned_row):
                        continue

                    all_rows.append(cleaned_row)

        merged_rows = merge_multiline_transactions(all_rows)

        for row in merged_rows:
            if len(row) < 4:
                continue

            date_str = row[0] if len (row) > 0 else ""
            if not re.match(r'\d{2}\.\d{2}\.\d{4}', date_str):
                continue

            category_or_desc = row[2] if len(row) > 2 else "" 
            description = row[3] if len(row) > 3 else ""

            amount_str = ""
            for col in row[3:5]:
                if col and any(c in col for c in "0123456789"):
                    amount_str = col
                    break
            
            if not amount_str:
                continue
            try:
                date = clean_date(date_str)
                amount = clean_amount(amount_str)
                full_description = f"{category_or_desc} | {description}" if description else category_or_desc
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