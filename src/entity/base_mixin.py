from datetime import datetime
from sqlalchemy import Column, func, DateTime,String
from sqlalchemy.event import listens_for


class BaseMixin:
    _table_args_ = {'extend_existing': True}
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


@listens_for(BaseMixin, 'before_update', propagate=True)
def update_updated_at(mapper, connection, target):
    target.updated_at = datetime.utcnow()