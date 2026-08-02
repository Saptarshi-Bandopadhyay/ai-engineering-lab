from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Central declarative base. All models will inherit from this.
    """
