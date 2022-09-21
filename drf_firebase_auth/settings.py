# -*- coding: utf-8 -*-
""" Settings config for the drf_firebase_auth application """
import os

from django.conf import settings
from rest_framework.settings import APISettings

from .utils import map_firebase_uid_to_username, get_firebase_user_email

USER_SETTINGS = getattr(settings, 'DRF_FIREBASE_AUTH', None)

DEFAULTS = {
    # sets logging level correct values are ERROR, WARNING, INFO and DEBUG
    'DRF_LOG_LEVEL': os.getenv('DRF_LOG_LEVEL', 'ERROR'),
    # allow anonymous requests without Authorization header set
    'ALLOW_ANONYMOUS_REQUESTS': os.getenv('ALLOW_ANONYMOUS_REQUESTS', False),
    # path to JSON file with firebase secrets
    'FIREBASE_SERVICE_ACCOUNT_KEY':
        os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY', ''),
    # allow creation of new local user in db
    'FIREBASE_CREATE_LOCAL_USER':
        os.getenv('FIREBASE_CREATE_LOCAL_USER', True),
    # attempt to split firebase user.display_name and set local user
    # first_name and last_name
    'FIREBASE_ATTEMPT_CREATE_WITH_DISPLAY_NAME':
        os.getenv('FIREBASE_ATTEMPT_CREATE_WITH_DISPLAY_NAME', True),
    # commonly JWT or Bearer (e.g. JWT <token>)
    'FIREBASE_AUTH_HEADER_PREFIX':
        os.getenv('FIREBASE_AUTH_HEADER_PREFIX', 'JWT'),
    # verify that JWT has not been revoked
    'FIREBASE_CHECK_JWT_REVOKED':
        os.getenv('FIREBASE_CHECK_JWT_REVOKED', True),
    # require that firebase user.email_verified is True
    'FIREBASE_AUTH_EMAIL_VERIFICATION':
        os.getenv('FIREBASE_AUTH_EMAIL_VERIFICATION', False),
    # function should accept firebase_admin.auth.UserRecord as argument
    # and return str
    'FIREBASE_USERNAME_MAPPING_FUNC': map_firebase_uid_to_username,
    # Local user unique field that will be used to map firebase user to local user
    # Possible options are 'Email' and 'PhoneNumber'.
    'FIREBASE_UNIQUE_USER_FIELD_MAPPING_FUNC': get_firebase_user_email,
    'FIREBASE_UNIQUE_USER_FIELD_NAME': 'email',
    'LOCAL_UNIQUE_USER_FIELD_NAME': 'email',
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
