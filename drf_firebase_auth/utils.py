""" helper functions """
from typing import Any
import uuid

from firebase_admin import auth


def get_firebase_user_email(firebase_user: auth.UserRecord) -> str:
    try:
        return (
            firebase_user.email
            if firebase_user.email
            else firebase_user.provider_data[0].email
        )
    except Exception as e:
        raise Exception(e)


def map_firebase_to_username_legacy(firebase_user: auth.UserRecord) -> str:
    try:
        username = '_'.join(
            firebase_user.display_name.split(' ')
            if firebase_user.display_name
            else str(uuid.uuid4())
        )
        return username if len(username) <= 30 else username[:30]
    except Exception as e:
        raise Exception(e)


def map_firebase_display_name_to_username(
    firebase_user: auth.UserRecord
) -> str:
    try:
        return '_'.join(firebase_user.display_name.split(' '))
    except Exception as e:
        raise Exception(e)


def map_firebase_uid_to_username(
    firebase_user: auth.UserRecord
) -> str:
    try:
        return firebase_user.uid
    except Exception as e:
        raise Exception(e)


def map_firebase_email_to_username(
    firebase_user: auth.UserRecord
) -> str:
    try:
        return get_firebase_user_email(firebase_user)
    except Exception as e:
        raise Exception(e)


def map_uuid_to_username(
    _: auth.UserRecord
) -> str:
    try:
        return str(uuid.uuid4())
    except Exception as e:
        raise Exception(e)
