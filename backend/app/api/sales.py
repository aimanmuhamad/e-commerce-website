from email.generator import Generator

from fastapi import status
from fastapi.params import Depends
from fastapi.routing import APIRouter

from app.core.logger import logger
from app.deps.db import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User
from app.schemas.request_params import DefaultResponse
from app.schemas.sale import GetSales

router = APIRouter()


@router.get("", response_model=GetSales, status_code=status.HTTP_200_OK)
def get_sales(
    session: Generator = Depends(get_db),
):

    finished_order = (
        session.query(Order, OrderItem)
        .join(OrderItem)
        .filter(Order.status == "finished")
        .all()
    )

    total_sold = sum([item.quantity for order, item in finished_order])

    return GetSales(data={"total": total_sold})
