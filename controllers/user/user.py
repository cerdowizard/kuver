from http.client import HTTPException

from fastapi import APIRouter


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database.database import get_db
from utils import oauth2
user_router = APIRouter(
    prefix="/api/v1/users",
)


@user_router.get('/profile')
def get_user_profile(db: Session = Depends(get_db), user_id: str = Depends(oauth2.require_user)):
    payload =  db.query(models.User).filter(models.User.id == user_id).first()
    if not payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in the database")

    else:
        return payload

