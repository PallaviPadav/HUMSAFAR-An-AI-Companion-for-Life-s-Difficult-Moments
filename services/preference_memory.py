from typing import Dict, List

from utils.logger import get_logger

from services.preference_extractor import (
    preference_extractor,
    PreferenceExtractionState,
)


logger = get_logger(__name__)


# =========================================================
# In-Memory Preference Store
# =========================================================

_preference_store: Dict[str, Dict[str, List[str]]] = {}


# =========================================================
# Empty Preference Structure
# =========================================================


def _empty_preferences():
    return {
        "hobbies": [],
        "activities": [],
        "interests": [],
        "favorite_categories": [],
        "dislikes": [],
        "communication_preferences": [],
    }


# =========================================================
# Get Preferences
# =========================================================


def get_preferences(conversation_id: str):
    if conversation_id not in _preference_store:
        _preference_store[conversation_id] = _empty_preferences()

        logger.info("Created preference memory for conversation: %s", conversation_id)

    return _preference_store[conversation_id]


# =========================================================
# Add Unique Preference
# =========================================================


def _add_unique(values: List[str], new_value: str):
    if not new_value:
        return

    new_value = new_value.strip()

    if not new_value:
        return

    existing = {value.lower() for value in values}

    if new_value.lower() not in existing:
        values.append(new_value)


# =========================================================
# Merge Extracted Preferences
# =========================================================


def _merge_preferences(stored_preferences, extracted: PreferenceExtractionState):
    categories = [
        "hobbies",
        "activities",
        "interests",
        "favorite_categories",
        "dislikes",
        "communication_preferences",
    ]

    for category in categories:
        extracted_values = getattr(extracted, category, [])

        for value in extracted_values:
            _add_unique(stored_preferences[category], value)


# =========================================================
# Update Preference Memory
# =========================================================


def update_preferences(conversation_id: str, user_message: str):
    logger.info("Updating preference memory for conversation: %s", conversation_id)

    # -----------------------------------------
    # Extract preferences using LLM
    # -----------------------------------------

    extracted = preference_extractor.extract(user_message)

    logger.info("Extracted preferences: %s", extracted)

    # -----------------------------------------
    # Get existing memory
    # -----------------------------------------

    preferences = get_preferences(conversation_id)

    # -----------------------------------------
    # Update only if stable preferences exist
    # -----------------------------------------

    if extracted.has_preferences:
        _merge_preferences(preferences, extracted)

        logger.info("Preference memory updated: %s", preferences)

    else:
        logger.info("No stable preferences found in message.")

    return (preferences, extracted)
