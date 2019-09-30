# -*- coding: utf-8 -*-
"""
Settings config for the drf_firebase_auth application
Author: Gary Burgmann
Email: garyburgmann@gmail.com
Location: Springfield QLD, Australia
Last update: 2019-02-10
"""
import datetime

from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, 'DRF_FIREBASE_AUTH', None)

DEFAULTS = {
    # allow anonymous requests without Authorization header set
    'ALLOW_ANONYMOUS_REQUESTS': False,
    # path to JSON file with firebase secrets
    'FIREBASE_SERVICE_ACCOUNT_KEY': '',
    # allow creation of new local user in db
    'FIREBASE_CREATE_LOCAL_USER': True,
    # attempt to split firebase user.display_name and set local user
    # first_name and last_name
    'FIREBASE_ATTEMPT_CREATE_WITH_DISPLAY_NAME': True,
    # commonly JWT or Bearer (e.g. JWT <token>)
    'FIREBASE_AUTH_HEADER_PREFIX': 'JWT',
    # verify that JWT has not been revoked
    'FIREBASE_CHECK_JWT_REVOKED': True,
    # require that firebase user.email_verified is True
    'FIREBASE_AUTH_EMAIL_VERIFICATION': False
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
