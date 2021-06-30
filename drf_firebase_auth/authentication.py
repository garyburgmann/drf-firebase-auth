# -*- coding: utf-8 -*-
"""
Authentication backend for handling firebase user.idToken from incoming
Authorization header, verifying, and locally authenticating
"""
from typing import Tuple, Dict
import logging

import firebase_admin
from firebase_admin import auth as firebase_auth
from django.utils.encoding import smart_text
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework import (
    authentication,
    exceptions
)

from .settings import api_settings
from .models import (
    FirebaseUser,
    FirebaseUserProvider
)
from . import __title__

log = logging.getLogger(__title__)
User = get_user_model()

firebase_credentials = firebase_admin.credentials.Certificate(
    api_settings.FIREBASE_SERVICE_ACCOUNT_KEY
)
firebase = firebase_admin.initialize_app(
    credential=firebase_credentials,
)


class FirebaseAuthentication(authentication.TokenAuthentication):
    """
    Token based authentication using firebase.
    """
    keyword = api_settings.FIREBASE_AUTH_HEADER_PREFIX

    def authenticate_credentials(
        self,
        token: str
    ) -> Tuple[AnonymousUser, Dict]:
        try:
            decoded_token = self._decode_token(token)
            firebase_user = self._authenticate_token(decoded_token)
            local_user = self._get_or_create_local_user(firebase_user)
            self._create_local_firebase_user(local_user, firebase_user)
            return (local_user, decoded_token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(e)

    def _decode_token(self, token: str) -> Dict:
        """
        Attempt to verify JWT from Authorization header with Firebase and
        return the decoded token
        """
        try:
            decoded_token = firebase_auth.verify_id_token(
                token,
                check_revoked=api_settings.FIREBASE_CHECK_JWT_REVOKED
            )
            log.info(f'_decode_token - decoded_token: {decoded_token}')
            return decoded_token
        except firebase_auth.ExpiredIdTokenError as e:
            if not api_settings.FIREBASE_IGNORE_JWT_EXPIRED:
                log.error(f'_decode_token - Exception: {e}')
                raise Exception(e)
            else:
                log.warn(f'_decode_token - Exception: {e}')
        except Exception as e:
            log.error(f'_decode_token - Exception: {e}')
            raise Exception(e)

    def _authenticate_token(
        self,
        decoded_token: Dict
    ) -> firebase_auth.UserRecord:
        """ Returns firebase user if token is authenticated """
        try:
            uid = decoded_token.get('uid')
            log.info(f'_authenticate_token - uid: {uid}')
            firebase_user = firebase_auth.get_user(uid)
            log.info(f'_authenticate_token - firebase_user: {firebase_user}')
            if api_settings.FIREBASE_UNIQUE_USER_FIELD_NAME == 'email' and api_settings.FIREBASE_AUTH_EMAIL_VERIFICATION:
                if not firebase_user.email_verified:
                    raise Exception(
                        'Email address of this user has not been verified.'
                    )
            return firebase_user
        except Exception as e:
            log.error(f'_authenticate_token - Exception: {e}')
            raise Exception(e)

    def _get_or_create_local_user(
        self,
        firebase_user: firebase_auth.UserRecord
    ) -> User:
        """
        Attempts to return or create a local User from Firebase user data
        """
        unique_user_value = api_settings.FIREBASE_UNIQUE_USER_FIELD_MAPPING_FUNC(
            firebase_user)
        log.info(
            f'_get_or_create_local_user - unique user value: {unique_user_value}')
        user = None
        try:
            kargs = {
                api_settings.LOCAL_UNIQUE_USER_FIELD_NAME: unique_user_value}
            user = User.objects.get(**kargs)
            log.info(
                f'_get_or_create_local_user - user.is_active: {user.is_active}'
            )
            if not user.is_active:
                raise Exception(
                    'User account is not currently active.'
                )
            user.last_login = timezone.now()
            user.save()
        except User.DoesNotExist as e:
            log.error(
                f'_get_or_create_local_user - User.DoesNotExist: {unique_user_value}'
            )
            if not api_settings.FIREBASE_CREATE_LOCAL_USER:
                raise Exception('User is not registered to the application.')
            username = \
                api_settings.FIREBASE_USERNAME_MAPPING_FUNC(firebase_user)
            log.info(
                f'_get_or_create_local_user - username: {username}'
            )
            try:
                kargs[api_settings.LOCAL_UNIQUE_USER_FIELD_NAME] = username
                user = User.objects.create_user(**kargs)
                user.last_login = timezone.now()
                if (
                    api_settings.FIREBASE_ATTEMPT_CREATE_WITH_DISPLAY_NAME
                    and firebase_user.display_name is not None
                ):
                    display_name = firebase_user.display_name.split(' ')
                    if len(display_name) == 2:
                        user.first_name = display_name[0]
                        user.last_name = display_name[1]
                user.save()
            except Exception as e:
                raise Exception(e)
        print('user', user.phone_number)
        return user

    def _create_local_firebase_user(
        self,
        user: User,
        firebase_user: firebase_auth.UserRecord
    ):
        """ Create a local FireBase model if one does not already exist """
        # pylint: disable=no-member
        local_firebase_user = FirebaseUser.objects.filter(
            user=user
        ).first()

        if not local_firebase_user:
            new_firebase_user = FirebaseUser(
                uid=firebase_user.uid,
                user=user
            )
            new_firebase_user.save()
            local_firebase_user = new_firebase_user

        if local_firebase_user.uid != firebase_user.uid:
            local_firebase_user.uid = firebase_user.uid
            local_firebase_user.save()

        # store FirebaseUserProvider data
        for provider in firebase_user.provider_data:
            local_provider = FirebaseUserProvider.objects.filter(
                provider_id=provider.provider_id,
                firebase_user=local_firebase_user
            ).first()
            if not local_provider:
                new_local_provider = FirebaseUserProvider.objects.create(
                    provider_id=provider.provider_id,
                    uid=provider.uid,
                    firebase_user=local_firebase_user,
                )
                new_local_provider.save()

        # catch locally stored providers no longer associated at Firebase
        local_providers = FirebaseUserProvider.objects.filter(
            firebase_user=local_firebase_user
        )
        if len(local_providers) != len(firebase_user.provider_data):
            current_providers = \
                [x.provider_id for x in firebase_user.provider_data]
            for provider in local_providers:
                if provider.provider_id not in current_providers:
                    FirebaseUserProvider.objects.filter(
                        id=provider.id
                    ).delete()
