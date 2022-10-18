from typing import Any, Generator

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.exc import DatabaseError
from starlette.responses import Response

from app.core.logger import logger
from app.deps.authentication import get_current_active_admin, get_current_active_user
from app.deps.db import get_db
from app.models.user import User
from app.schemas.request_params import DefaultResponse
from app.schemas.user import (
    DeleteUser,
    GetUser,
    GetUserAddress,
    GetUserBalance,
    PutUserBalance,
)

router = APIRouter()


@router.get("", response_model=GetUser, status_code=status.HTTP_200_OK)
async def get_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return current_user.User


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_user(
    session: Generator = Depends(get_db),
) -> Any:
    user = session.query(User).all()

    return user


@router.get(
    "/shipping_address", response_model=GetUserAddress, status_code=status.HTTP_200_OK
)
async def get_user_shipping_address(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return current_user.User


@router.put(
    "/shipping_address", response_model=DefaultResponse, status_code=status.HTTP_200_OK
)
async def put_user_shipping_address(
    request: GetUserAddress,
    session: Generator = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    current_user.User.address_name = request.address_name
    current_user.User.address = request.address
    current_user.User.city = request.city
    current_user.User.phone_number = request.phone_number

    session.commit()

    logger.info(f"User {current_user.User.email} updated shipping address")
    return DefaultResponse(message="Shipping address updated")


@router.get("/balance", response_model=GetUserBalance, status_code=status.HTTP_200_OK)
async def get_user_balance(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return current_user.User


@router.put(
    "/balance", response_model=DefaultResponse, status_code=status.HTTP_201_CREATED
)
async def put_user_balance(
    request: PutUserBalance,
    session: Generator = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    new_balance = int(current_user.User.balance) + request.balance
    current_user.User.balance = new_balance
    session.commit()
    logger.info(f"User {current_user.User.email} updated balance")
    return DefaultResponse(
        message=f"Your balance has been updated, current_balance:{new_balance}"
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: DeleteUser,
    session: Generator = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
) -> Response:
    try:
        session.query(User).filter(User.id == request.id).delete()
        session.commit()
    except DatabaseError as e:
        error = (
            e.orig.args[0]
            .split("DETAIL:")[1]
            .strip()
            .replace('"', "")
            .replace("\\", "")
        )
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{error}"
        )
    logger.info(f"User {request.id} deleted by {current_user.User.email}")
