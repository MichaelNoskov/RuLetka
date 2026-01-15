from sqlalchemy import Column, String, Boolean, Date

from .meta import Base, IDMixin


class User(Base, IDMixin):
    __tablename__ = "user"

    username = Column(
        String(50), 
        unique=True, 
        index=True,
        nullable=False
    )
    password = Column(
        String(128),
        nullable=False
    )
    is_male = Column(
        Boolean,
        comment="Пол пользователя (True - мужской, False - женский)"
    )
    birthdate = Column(
        Date
    )
    country = Column(
        String(50)
    )
    description = Column(
        String(500)
    )
