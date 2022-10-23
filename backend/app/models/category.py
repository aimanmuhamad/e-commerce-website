from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import Column, ForeignKey, String

from app.db import Base
from app.models.default import DefaultModel


class Category(DefaultModel, Base):
    __tablename__ = "categories"

    title = Column(String(length=64), nullable=False, unique=True)
    image_id = Column(ForeignKey("images.id", ondelete="CASCADE"), nullable=False)

    @classmethod
    def seed(cls, fake, category, image_id):
        category = Category(
            id=fake.uuid4(),
            title=category,
            image_id=image_id,
        )
        return category
