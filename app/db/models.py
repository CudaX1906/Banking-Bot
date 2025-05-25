from sqlalchemy import (
    Column, String, DateTime, Boolean, ForeignKey,
    Enum, Numeric, Index, JSON, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from . import Base
import uuid
from datetime import datetime
from .schemas import SenderEnum, TransactionStatusEnum


class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    fallback_requests = relationship("FallbackHelpRequest", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_users_email_phone', 'email', 'phone_number'),
    )


class ChatSession(Base):
    __tablename__ = 'sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    fallback_requests = relationship("FallbackHelpRequest", back_populates="session", cascade="all, delete-orphan")
    agent_events = relationship("AgentEvent", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_sessions_user_id', 'user_id'),
    )


class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id'), nullable=False)
    sender = Column(Enum(SenderEnum), nullable=False)
    content = Column(String, nullable=False)
    message_metadata = Column(JSONB,nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")

    __table_args__ = (
        Index('ix_messages_session_id', 'session_id'),
    )


class Account(Base):
    __tablename__ = 'accounts'

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    account_number = Column(String, unique=True, nullable=False)
    account_type = Column(String, nullable=False)  # e.g., SAVINGS, CURRENT
    balance = Column(Numeric(15, 2), nullable=False, default=0.00)
    currency = Column(String, default='INR', nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="from_account", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_account_user_number', 'user_id', 'account_number'),
    )


class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.account_id'), nullable=False)
    to_account_number = Column(String, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(TransactionStatusEnum), nullable=False)
    reference_id = Column(String, unique=True, nullable=True)
    message_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    from_account = relationship("Account", back_populates="transactions")

    __table_args__ = (
        Index('ix_transaction_from_account', 'from_account_id'),
    )


class FallbackHelpRequest(Base):
    __tablename__ = 'fallback_help_requests'

    help_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id'), nullable=False)

    notes = Column(Text)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="fallback_requests")
    session = relationship("ChatSession", back_populates="fallback_requests")

    __table_args__ = (
        Index('ix_fallback_help_user', 'user_id', 'session_id'),
    )


class AgentEvent(Base):
    __tablename__ = 'agent_events'

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id'), nullable=False)
    agent_name = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # e.g., STARTED, COMPLETED, FAILED
    payload = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="agent_events")

    __table_args__ = (
        Index('ix_agent_event_session', 'session_id'),
    )
