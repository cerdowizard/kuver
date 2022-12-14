from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database.database import get_db

transac_router = APIRouter(
    prefix="/api/v1/transactions",
)


@transac_router.post('/create', status_code=status.HTTP_201_CREATED)
def create_transaction(payload: schemas.CreateNewTransaction, db: Session = Depends(get_db)):
    """
    Create a new transaction
    """

    base_price = db.query(models.Currency).filter(models.Currency.price == payload.base_price).first()

    if base_price.price == payload.base_price:
        new_price = base_price.price * payload.amount
        return {
            payload.amount,
            payload.account_name,
            new_price
        }
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")

    # new_price = models.Transaction(**payload.dict())
    # db.add(new_price)
    # db.commit()
    # db.refresh(new_price)



@transac_router.get('/all/transactions')
def get_all_transactions(db: Session = Depends(get_db)):
    """
        Get all transactions from the database
    """
    payload_result = db.query(models.Transaction).all()
    return payload_result


@transac_router.get('/transaction/{id}')
def get_transaction_by_id(transaction_id: int, db: Session = Depends(get_db)):
    """
        Get transactions by id from the database
    """
    payload = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if payload != transaction_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return payload
