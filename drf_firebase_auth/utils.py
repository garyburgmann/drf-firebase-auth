""" helper functions """
from typing import Any
import uuid

from firebase_admin import auth


def get_firebase_user_uid(firebase_user: auth.UserRecord) -> str:
    try:
        if firebase_user.uid:
            return firebase_user.uid
    except Exception as e:
        raise Exception(e)


def get_firebase_user_identifier(firebase_user: auth.UserRecord) -> str:
    try:
        if firebase_user.email:
            return firebase_user.email
        elif firebase_user.provider_data[0].email:
            return firebase_user.provider_data[0].email
        elif firebase_user.phone_number:
            return firebase_user.phone_number
        elif firebase_user.provider_data[0].phone_number:
            return firebase_user.provider_data[0].phone_number
        else:
            raise Exception("Identifier not found, this would fail authentication process")
    except Exception as e:
        raise Exception(e)


def map_firebase_uid_to_username(
    firebase_user: auth.UserRecord
) -> str:
    try:
        return firebase_user.uid
    except Exception as e:
        raise Exception(e)
