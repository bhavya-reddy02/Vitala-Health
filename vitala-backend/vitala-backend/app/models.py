"""Relational schema (PostgreSQL).

users ──1:1── health_profiles
   │
   ├──1:1── user_progress         (denormalised XP/streak for fast reads)
   ├──1:N── quest_completions     (event log; one row per quest per day)
   └──1:N── badge_unlocks         (one row per badge a user has earned)
"""
from datetime import datetime, date

from sqlalchemy import (
    String, Integer, Float, Date, DateTime, Text, ForeignKey, JSON,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profile: Mapped["HealthProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan")
    progress: Mapped["UserProgress"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan")
    completions: Mapped[list["QuestCompletion"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    badge_unlocks: Mapped[list["BadgeUnlock"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    learning: Mapped[list["LearningProgress"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column(String(80), default="")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sex: Mapped[str] = mapped_column(String(20), default="")
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    goal: Mapped[str] = mapped_column(String(20), default="active")
    activity: Mapped[str] = mapped_column(String(20), default="mid")
    focus: Mapped[list] = mapped_column(JSON, default=list)  # e.g. ["hydration","movement"]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="profile")


class UserProgress(Base):
    __tablename__ = "user_progress"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_quests: Mapped[int] = mapped_column(Integer, default=0)
    perfect_days: Mapped[int] = mapped_column(Integer, default=0)
    cat_counts: Mapped[dict] = mapped_column(JSON, default=dict)   # {"hydration": 3, ...}
    perfect_dates: Mapped[list] = mapped_column(JSON, default=list)  # ["2026-07-01", ...]
    joined_date: Mapped[date] = mapped_column(Date, default=date.today)

    user: Mapped[User] = relationship(back_populates="progress")


class QuestCompletion(Base):
    __tablename__ = "quest_completions"
    __table_args__ = (UniqueConstraint("user_id", "quest_id", "quest_date", name="uq_quest_per_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quest_id: Mapped[str] = mapped_column(String(40))
    quest_date: Mapped[date] = mapped_column(Date, index=True)
    xp_awarded: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="completions")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(12))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="chat_messages")


class BadgeUnlock(Base):
    __tablename__ = "badge_unlocks"
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_badge_per_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    badge_id: Mapped[str] = mapped_column(String(40))
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="badge_unlocks")


class LearningProgress(Base):
    __tablename__ = "learning_progress"
    __table_args__ = (UniqueConstraint("user_id", "module_id", name="uq_module_per_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    module_id: Mapped[str] = mapped_column(String(40))
    cards_completed: Mapped[bool] = mapped_column(default=False)
    quiz_completed: Mapped[bool] = mapped_column(default=False)
    best_score: Mapped[int] = mapped_column(Integer, default=0)   # best quiz score, %
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0)   # total XP given for this module
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="learning")
