# app/optimization_engine.py

import copy


# ----------------------------------------
# Instructor Candidate Scoring
# ----------------------------------------

def score_instructor_candidate(slot, instructor):

    score = 0

    # Prefer lower duty load if field exists
    if hasattr(instructor, "current_duty_hours"):
        score += instructor.current_duty_hours

    # Prefer higher rating if exists
    if hasattr(instructor, "rating"):
        score -= instructor.rating

    return score


def select_best_instructor(slot, instructors, unavailable_id):

    candidates = []

    for instructor in instructors:

        if instructor.instructor_id == unavailable_id:
            continue

        if not hasattr(instructor, "availability"):
            continue

        available = False
        for entry in instructor.availability:
            if entry["slot_id"] == slot["slot_id"]:
                available = True
                break

        if not available:
            continue

        score = score_instructor_candidate(slot, instructor)
        candidates.append((score, instructor))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


# ----------------------------------------
# Slot Change Cost Function
# ----------------------------------------

def calculate_slot_cost(old_slot, new_slot):

    cost = 0

    if old_slot["activity"] != new_slot["activity"]:
        cost += 5

    if old_slot["instructor_id"] != new_slot["instructor_id"]:
        cost += 4

    if old_slot["resource_id"] != new_slot["resource_id"]:
        cost += 3

    if old_slot["dispatch_decision"] != new_slot["dispatch_decision"]:
        cost += 2

    return cost