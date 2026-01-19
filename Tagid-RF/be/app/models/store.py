"""
SQLAlchemy models for store management.
"""

from app.services.database import Base
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Store(Base):
    """Store/branch model for multi-store management."""

    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="Store name")
    address = Column(String(255), nullable=True, comment="Physical address")
    phone = Column(String(20), nullable=True, comment="Contact phone")

    is_active = Column(
        Boolean, default=True, nullable=False, index=True, comment="Store active status"
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    users = relationship("User", back_populates="store")


class User(Base):
    """User model with role-based access control."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="Full name")
    email = Column(
        String(255), unique=True, nullable=False, index=True, comment="Email address"
    )
    phone = Column(String(20), nullable=True, comment="Phone number")
    password_hash = Column(String(255), nullable=True, comment="Hashed password")

    # Role: ADMIN (chain), MANAGER (store), SELLER, CUSTOMER
    role = Column(
        String(20),
        nullable=False,
        default="CUSTOMER",
        index=True,
        comment="User role: ADMIN, MANAGER, SELLER, CUSTOMER",
    )

    # Store assignment (null for ADMIN and CUSTOMER)
    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Assigned store",
    )

    is_active = Column(
        Boolean, default=True, nullable=False, index=True, comment="User active status"
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    store = relationship("Store", back_populates="users")
    notification_preferences = relationship(
        "NotificationPreference", back_populates="user"
    )


class NotificationPreference(Base):
    """User notification preferences for different channels."""

    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this preference",
    )

    # Notification type
    notification_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type: UNPAID_EXIT, SALE, LOW_STOCK, GOAL_ACHIEVED, SYSTEM_UPDATE, NEW_USER, ERROR",
    )

    # Channels
    channel_push = Column(
        Boolean, default=True, nullable=False, comment="Push notification enabled"
    )
    channel_sms = Column(
        Boolean, default=False, nullable=False, comment="SMS notification enabled"
    )
    channel_email = Column(
        Boolean, default=False, nullable=False, comment="Email notification enabled"
    )

    # For ADMIN: filter by specific store (null = all stores)
    store_filter_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="SET NULL"),
        nullable=True,
        comment="Filter notifications to specific store (ADMIN only)",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="notification_preferences")


class Notification(Base):
    """Notification log - records all sent notifications."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Who and what
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    notification_type = Column(String(50), nullable=False, index=True)

    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Channels sent through
    sent_push = Column(Boolean, default=False, nullable=False)
    sent_sms = Column(Boolean, default=False, nullable=False)
    sent_email = Column(Boolean, default=False, nullable=False)

    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    # Related entities
    store_id = Column(
        Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True
    )
    tag_epc = Column(
        String(128), nullable=True, comment="Related RFID tag EPC if applicable"
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    user = relationship("User")
