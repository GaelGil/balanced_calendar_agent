from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


class ChatSession(db.Model):
    __tablename__ = "chat_sessions"
    id = db.Column(db.Integer, primary_key=True)  # SERIAL integer
    user_id = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )
    tool_history = db.relationship(
        "ToolHistory", back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("chat_sessions.id"), nullable=False
    )
    role = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session = db.relationship("ChatSession", back_populates="messages")


# TODO: RUNN MIGRATIONS for removing userid
class ToolHistory(db.Model):
    __tablename__ = "tool_history"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("chat_sessions.id"), nullable=False
    )
    tool_name = db.Column(db.String, nullable=False)
    tool_input = db.Column(JSON)  # <-- use JSON type
    tool_output = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session = db.relationship("ChatSession", back_populates="tool_history")
