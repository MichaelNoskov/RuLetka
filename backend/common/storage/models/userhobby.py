from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column

from common.storage.models.meta import Base, UUIDMixin


class UserHobby(Base, UUIDMixin):
    __tablename__ = 'userhobby'

    user_id = mapped_column('user', ForeignKey('user.id'), nullable=False)
    hobby_id = mapped_column('hobby', ForeignKey('hobby.id'), nullable=False)

    __table_args__ = (UniqueConstraint('user', 'hobby', name='uq_user_hobby'),)
