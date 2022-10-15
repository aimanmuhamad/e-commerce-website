from sqlalchemy import Column, ForeignKey, Integer

from app.db import Base
from app.models.default import DefaultModel


class OrderItem(DefaultModel, Base):
    __tablename__ = "order_items"

    quantity = Column(Integer, nullable=False)
    order_id = Column(ForeignKey("orders.id"), nullable=False)
    product_size_quantity_id = Column(
        ForeignKey("product_size_quantities.id"), nullable=False
    )

    @classmethod
    def seed(cls, fake, order_id, product_size_quantity_id):
        order_item = OrderItem(
            id=fake.uuid4(),
            quantity=fake.pyint(max_value=10),
            order_id=order_id,
            product_size_quantity_id=product_size_quantity_id,
        )
        return order_item
