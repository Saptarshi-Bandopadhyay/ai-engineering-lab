# Import all models here so Alembic can discover them via a single import
from backend.app.db.base import Base as Base
from backend.app.models.user import User as User

# This allows: `from app.models import Base` in your Alembic env.py
