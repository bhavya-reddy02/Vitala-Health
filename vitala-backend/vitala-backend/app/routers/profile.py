"""/profile — health profile + the full dashboard state."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..security import get_current_user
from ..serializers import serialize_state
from .. import models, schemas

router = APIRouter(prefix="/profile", tags=["profile"])


@router.put("")
def upsert_profile(
    body: schemas.ProfileIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create the health profile during onboarding, or update it later."""
    profile = user.profile
    if profile is None:
        profile = models.HealthProfile(user_id=user.id)
        db.add(profile)

    profile.name = body.name
    profile.age = body.age
    profile.sex = body.sex
    profile.height_cm = body.height_cm
    profile.weight_kg = body.weight_kg
    profile.goal = body.goal
    profile.activity = body.activity
    profile.focus = body.focus
    db.commit()
    db.refresh(user)
    return serialize_state(user, db)


@router.get("")
def get_state(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Everything the dashboard needs in one call."""
    return serialize_state(user, db)
