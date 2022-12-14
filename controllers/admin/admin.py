import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database.database import get_db
from utils import oauth2

admin_router = APIRouter(
    prefix="/api/v1/admin",
)


@admin_router.get('/get/all-users')
def get_all_users(db: Session = Depends(get_db),user_id: str = Depends(oauth2.require_admin)):
    """
    get all user from the database a new
    """
    payload = db.query(models.User).all()
    return payload


@admin_router.get('/get/all-transaction')
def get_all_transaction(db: Session = Depends(get_db), user_id: str = Depends(oauth2.require_super_admin)):
    """
      get all Transaction from the database a new
      """
    payload = db.query(models.Transaction).all()
    return payload


@admin_router.put('/update/user/{id}')
def update_user(id: uuid.UUID, payload: schemas.UpdateUser, db: Session = Depends(get_db)):
    """
    update user role 
    """
    result = db.query(models.User).filter(models.User.id == id)
    get_role = db.query(models.User).filter(models.User.role == payload).first()
    # if get_role == payload.role:
    #     raise HTTPException(status_code=status.HTTP_200_OK, detail=f"user {id} is already {payload.role}")
    # if payload.role != 'user' or payload.role != 'admin':
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not allowed")
    if result.role == payload.role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not allowed")

    if not result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="id is not a valid user")
    result.update(payload.dict(), synchronize_session=False)

    db.commit()
    return f'User role has been updated successfully'


@admin_router.post('/create/price')
def create_new_price(payload: schemas.CreateNewPrice, db: Session = Depends(get_db)):
    new_price = models.Currency(**payload.dict())
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price
