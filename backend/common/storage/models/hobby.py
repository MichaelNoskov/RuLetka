from sqlalchemy import Column, String

from common.storage.models.meta import Base, UUIDMixin


class Hobby(Base, UUIDMixin):
    __tablename__ = "hobby"

    title = Column(String, unique=True, index=True)
    image = Column(String, nullable=True)
