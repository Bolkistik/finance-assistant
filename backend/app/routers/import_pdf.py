from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models
from ..core.security import get_current_user
from ..core.parsers import parse_sber_pdf

router = APIRouter(prefix="/api/import/pdf", tags=["import"])

@router.post('/preview')
async def preview_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Предосмотр транзакций из PDF без сохранения в БД"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    try:
        contents = await file.read()

        if len(contents) == 0:
            raise HTTPException(400, "Empty file")
        
        transactions = parse_sber_pdf(contents)

        if not transactions:
            raise HTTPException(400, "No transactions found in PDF")
        
        return {
            "transactions": transactions,
            "total": len(transactions),
            "message": f"Найдено {len(transactions)} транзакций"
        }
    
    except Exception as e:
        raise HTTPException(400, detail=f"Error parsing PDF: {str(e)}")
    
@router.post("/save")
async def save_transactions(
    transactions_data: List[dict],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Сохраняет транзакции в БД (после подтверждения пользователем)"""

    saved = 0
    errors = []
    """Получаем категории из БД для сопоставления"""
    categories = {c.name: c.id for c in db.query(models.Category).all()}
    default_category_id = categories.get("Прочее")

    for trans_data in transactions_data:
        try:
            category_name = trans_data.get("category_name", "Прочее")
            category_id = categories.get(category_name, default_category_id)

            transaction = models.Transaction(
                date=trans_data["date"],
                description =trans_data["description"],
                amount=trans_data["amount"],
                transaction_type=trans_data.get("transaction_type", "expense"),
                category_id=category_id,
                user_id=current_user.id
            )
            db.add(transaction)
            saved += 1
        
        except Exception as e:
            errors.append({"description": trans_data.get("description"), "error": str(e)})

    try: 
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(400, detail=f"Database error: {str(e)}")
    
    return {
        "saved" : saved,
        "errors" : errors,
        "message": f"Сохранено {saved} из {len(transactions_data)} транзакций"
    }