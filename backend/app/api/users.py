from typing import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from starlette.responses import Response

from app.core.logger import logger
from app.deps.authentication import get_current_active_admin, get_current_active_user
from app.deps.db import get_db
from app.deps.sql_error import format_error
from app.models.user import User
from app.schemas.default_model import DefaultResponse
from app.schemas.user import (
    DeleteUser,
    GetUser,
    GetUserAddress,
    GetUserBalance,
    PutUserAddress,
    PutUserBalance,
)

router = APIRouter()


@router.get("", response_model=GetUser, status_code=status.HTTP_200_OK)
def get_user(
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    return current_user


@router.get(
    "/shipping_address", response_model=GetUserAddress, status_code=status.HTTP_200_OK
)
def get_user_shipping_address(
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    return current_user


@router.get("/balance", response_model=GetUserBalance, status_code=status.HTTP_200_OK)
async def get_user_balance(
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    return current_user


@router.put("", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
def update_user(
    request: GetUser,
    current_user: User = Depends(get_current_active_admin),
    session: Generator = Depends(get_db),
) -> JSONResponse:
    try:
        session.query(User).filter(User.id == request.id).update(
            {
                "name": request.name,
                "email": request.email,
                "phone_number": request.phone_number,
                "address_name": request.address_name,
                "address": request.address,
                "city": request.city,
                "balance": request.balance,
            }
        )
        session.commit()
    except Exception as e:
        logger.error(format_error(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )

    return DefaultResponse(message="User updated successfully")


@router.put(
    "/shipping_address", response_model=DefaultResponse, status_code=status.HTTP_200_OK
)
def put_user_shipping_address(
    request: PutUserAddress,
    session: Generator = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    current_user.address_name = request.address_name
    current_user.address = request.address
    current_user.city = request.city
    current_user.phone_number = request.phone_number

    session.commit()

    logger.info(f"User {current_user.email} updated shipping address")
    return DefaultResponse(message="Shipping address updated")


@router.put(
    "/balance", response_model=DefaultResponse, status_code=status.HTTP_201_CREATED
)
def put_user_balance(
    request: PutUserBalance,
    session: Generator = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    new_balance = int(current_user.balance) + request.balance
    current_user.balance = new_balance
    try:
        session.commit()
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integer value out of range"
            if "integer out of range" in format_error(e)
            else format_error(e),
        )
    logger.info(f"User {current_user.email} updated balance")
    return DefaultResponse(
        message=f"Your balance has been updated, Current Balance: {new_balance}"
    )


@router.delete("", response_model=DefaultResponse, status_code=status.HTTP_200_OK)
def delete_user(
    id: UUID,
    session: Generator = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
) -> JSONResponse:
    try:
        session.query(User).filter(User.id == id).delete()
        session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=format_error(e),
        )

    if current_user.id == id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't delete yourself",
        )

    logger.info(f"User {id} deleted by {current_user.email}")

    return DefaultResponse(message="User deleted successfully")


@router.get("/{id}", response_model=GetUser, status_code=status.HTTP_200_OK)
def get_detail_user(
    id: UUID,
    current_user: User = Depends(get_current_active_admin),
    session: Generator = Depends(get_db),
) -> JSONResponse:
    user = session.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
