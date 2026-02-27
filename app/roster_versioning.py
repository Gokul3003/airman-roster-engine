# app/roster_versioning.py

from typing import Dict, List
from sqlalchemy.orm import Session
from app.models import RosterVersion


# ----------------------------------------
# Get Latest Roster Version
# ----------------------------------------

def get_latest_roster(db: Session):

    latest = (
        db.query(RosterVersion)
        .order_by(RosterVersion.created_at.desc())
        .first()
    )

    if latest:
        return latest.roster_snapshot

    return None


# ----------------------------------------
# Calculate Diff
# ----------------------------------------

def calculate_diff(old_roster: Dict, new_roster: Dict):

    changes = []

    for old_day, new_day in zip(old_roster["roster"], new_roster["roster"]):
        for old_slot, new_slot in zip(old_day["slots"], new_day["slots"]):
            if old_slot != new_slot:
                changes.append({
                    "date": old_day["date"],
                    "slot_id": old_slot["slot_id"],
                    "before": old_slot,
                    "after": new_slot
                })

    return changes


# ----------------------------------------
# Calculate Churn
# ----------------------------------------

def calculate_churn(old_roster: Dict, new_roster: Dict):

    total = 0
    changed = 0

    for old_day, new_day in zip(old_roster["roster"], new_roster["roster"]):
        for old_slot, new_slot in zip(old_day["slots"], new_day["slots"]):
            total += 1
            if old_slot != new_slot:
                changed += 1

    if total == 0:
        return 0

    return changed / total


# ----------------------------------------
# Save Version
# ----------------------------------------

def save_version(
    db: Session,
    correlation_id: str,
    roster_snapshot: Dict,
    diff: List[Dict],
    churn: float,
    violations: int
):

    version = RosterVersion(
        correlation_id=correlation_id,
        roster_snapshot=roster_snapshot,
        diff_json=diff,
        churn=churn,
        violation_count=violations
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return version


# ----------------------------------------
# Fetch Versions (Metadata Only)
# ----------------------------------------

def fetch_versions(db: Session):

    versions = db.query(RosterVersion).order_by(RosterVersion.created_at.desc()).all()

    return [
        {
            "id": v.id,
            "correlation_id": v.correlation_id,
            "created_at": v.created_at,
            "churn": v.churn,
            "violation_count": v.violation_count
        }
        for v in versions
    ]