"""Request and response shapes (Pydantic v2)."""
from pydantic import BaseModel, EmailStr, Field


# ---- auth ----
class SignupIn(BaseModel):
    username: str = Field(min_length=2, max_length=40)
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    has_profile: bool


# ---- profile ----
class ProfileIn(BaseModel):
    name: str = ""
    age: int | None = None
    sex: str = ""
    height_cm: float | None = None
    weight_kg: float | None = None
    goal: str = "active"
    activity: str = "mid"
    focus: list[str] = []


# ---- quests ----
class CompleteIn(BaseModel):
    quest_id: str


# ---- assistant ----
class ChatIn(BaseModel):
    message: str
    literacy: str | None = "standard"  # "simple" | "standard" | "detailed"


# ---- learning (Phase 3) ----
class QuizSubmitIn(BaseModel):
    answers: dict[str, int]  # { question_id: selected_option_index }
