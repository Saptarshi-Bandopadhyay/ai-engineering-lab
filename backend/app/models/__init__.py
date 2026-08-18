# Import all models here so Alembic can discover them via a single import
from backend.app.db.base import Base as Base
from backend.app.models.conversation import Conversation as Conversation
from backend.app.models.document import Document as Document
from backend.app.models.document import DocumentChunk as DocumentChunk
from backend.app.models.message import Message as Message
from backend.app.models.user import User as User

# This allows: `from app.models import Base` in your Alembic env.py
