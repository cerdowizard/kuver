from datetime import timedelta
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr
from sqlalchemy.orm import Session
from utils import password_encoder
import re
import models
import schemas
from config import settings
from database.database import get_db
from utils import oauth2
import random as ra

#


router = APIRouter(prefix='/api/auth')
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


# [...]
@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(payload: schemas.CreateUserSchema, db: Session = Depends(get_db)):
    # Check if user already exist
    user = db.query(models.User).filter(
        models.User.email == EmailStr(payload.email.lower())).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')
    # Compare password and passwordConfirm
    if payload.password != payload.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    if len(payload.mobile_number) < 11:
        raise HTTPException(status_code=400, detail="Phone number too short")
    elif len(payload.mobile_number) > 11:
        raise HTTPException(status_code=400, detail="Phone number too long")
    #  Hash the password
    if not re.match("^[0-9 \-]+$", payload.mobile_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Make sure you only use numbers")
    password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    # if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=.]{8,}', payload.password):

    if re.match(password_pattern, payload.password):
        pass
    else:
        raise HTTPException(status_code=400,
                            detail="password must not be less "
                                   "than 8 characters and "
                                   "must contain one "
                                   "capital letter, "
                                   "small letter and a symbol")

    payload.password = password_encoder.hash_password(payload.password)
    del payload.password_confirm
    payload.email = EmailStr(payload.email.lower())
    payload.country = str(payload.country.capitalize())
    new_user = models.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# [... Configurations ...]

# Register a new user

# Login user
@router.post('/login')
def login(payload: schemas.LoginUserSchema, response: Response, db: Session = Depends(get_db),
          Authorize: AuthJWT = Depends()):
    # Check if the user exist
    user = db.query(models.User).filter(
        models.User.email == EmailStr(payload.email.lower())).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect Email or Password')

    # Check if user verified his email
    if not user.verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Please verify your email address')

    # Check if the password is valid
    if not password_encoder.verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect Email or Password')

    # Create access token
    access_token = Authorize.create_access_token(
        subject=str(user.id), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=str(user.id), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))

    # Store refresh and access tokens in cookie
    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
                        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('refresh_token', refresh_token,
                        REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
                        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    # Send both access
    return {'status': 'success', 'access_token': access_token}


@router.get('/refresh')
def refresh_token(response: Response, request: Request, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_refresh_token_required()

        user_id = Authorize.get_jwt_subject()
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not refresh access token')
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='The user belonging to this token no logger exist')
        access_token = Authorize.create_access_token(
            subject=str(user.id), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Please provide refresh token')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
                        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
                        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
    return {'access_token': access_token}


@router.post('/forgot-password')
def forgot_password(payload: schemas.ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == EmailStr(payload.email.lower())).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found in the database")
    reset_code = ra.randint(8888, 999935)
    create_token = models.Reset_Token(
        email=payload.email,
        token=reset_code
    )
    db.add(create_token)
    db.commit()
    db.refresh(create_token)
    return f'Here is your reset_code {reset_code}'


@router.put('/verify-token', status_code=status.HTTP_201_CREATED)
def verify_token(token: str, payload: schemas.UpdatePassword, db: Session = Depends(get_db)):
    payload_token = db.query(models.Reset_Token).filter(models.Reset_Token == token)
    payload_email = db.query(models.User).filter(models.User.email == payload.email)

    if not payload_email.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found in the database")

    if not payload_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found in the database")

    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    del payload.passwordConfirm
    payload.password = password_encoder.hash_password(payload.password)
    payload_email.update(payload.dict(), synchronize_session=False)
    db.commit()
    return f'Password has been updated successfully'


@router.get('/logout', status_code=status.HTTP_200_OK)
def logout(response: Response, Authorize: AuthJWT = Depends(), user_id: str = Depends(oauth2.require_user)):
    Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}
