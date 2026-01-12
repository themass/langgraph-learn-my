from sqlalchemy import Column, String, Text, DateTime, JSON, Enum, LargeBinary, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class Session(Base):
    """
    Session metadata table.
    """
    __tablename__ = "sessions"

    session_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), index=True, nullable=False)
    topic = Column(Text, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AgentCheckpoint(Base):
    """
    LangGraph Checkpointer storage for MySQL.
    Mimics the schema required by LangGraph but adapted for MySQL.
    """
    __tablename__ = "agent_checkpoints"

    thread_id = Column(String(255), primary_key=True)
    thread_ts = Column(String(255), primary_key=True)
    parent_ts = Column(String(255), nullable=True)
    checkpoint = Column(LargeBinary, nullable=False) # Serialized state (msgpack/json)
    metadata_ = Column("metadata", JSON, nullable=True) # avoiding reserved keyword
    created_at = Column(DateTime(timezone=True), server_default=func.now())
