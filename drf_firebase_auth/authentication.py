# -*- coding: utf-8 -*-
"""
Authentication backend for handling firebase user.idToken from incoming
Authorization header, verifying, and locally authenticating
Author: Gary Burgmann
Email: garyburgmann@gmail.com
Location: Springfield QLD, Australia
Last update: 2019-02-10
"""
import json
import uuid

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

from drf_firebase_auth.settings import api_settings
from drf_firebase_auth.models import (
    FirebaseUser,
    FirebaseUserProvider
)

User = get_user_model()

firebase_credentials = firebase_admin.credentials.Certificate(
    api_settings.FIREBASE_SERVICE_ACCOUNT_KEY
)
firebase = firebase_admin.initialize_app(firebase_credentials)


class BaseFirebaseAuthentication(authentication.BaseAuthentication):
    """
    Token based authentication using firebase.
    """
    def authenticate(self, request):
        """
        With ALLOW_ANONYMOUS_REQUESTS, set request.user to an AnonymousUser, 
        allowing us to configure access at the permissions level.
        """
        authorization_header = authentication.get_authorization_header(request)
        if api_settings.ALLOW_ANONYMOUS_REQUESTS and not authorization_header:
            return (AnonymousUser(), None)

        """
        Returns a tuple of len(2) of `User` and the decoded firebase token if
        a valid signature has been supplied using Firebase authentication.
        """
        firebase_token = self.get_token(request)

        decoded_token = self.decode_token(firebase_token)

        firebase_user = self.authenticate_token(decoded_token)

        local_user = self.get_or_create_local_user(firebase_user)

        self.create_local_firebase_user(local_user, firebase_user)
        # authenicated_user = self.authenticate_user(firebase_user)

        return (local_user, decoded_token)

    def get_token(self, request):
        raise NotImplementedError('get_token() has not been implemented.')

    def decode_token(self, firebase_token):
        raise NotImplementedError('decode_token() has not been implemented.')

    def authenticate_token(self, decoded_token):
        raise NotImplementedError('authenticate_token() has not been implemented.')

    def get_or_create_local_user(self, firebase_user):
        raise NotImplementedError('get_or_create_local_user() has not been implemented.')

    def create_local_firebase_user(self, local_user, firebase_user):
        raise NotImplementedError('create_local_firebase_user() has not been implemented.')


class FirebaseAuthentication(BaseFirebaseAuthentication):
    """
    Clients should authenticate by passing the token key in the
    'Authorization' HTTP header, prepended with the string specified in the
    settings.FIREBASE_AUTH_HEADER_PREFIX setting (Default = 'JWT')
    """
    www_authenticate_realm = 'api'

    def get_token(self, request):
        """
        Parse Authorization header and retrieve JWT
        """
        authorization_header = \
            authentication.get_authorization_header(request).split()
        auth_header_prefix = api_settings.FIREBASE_AUTH_HEADER_PREFIX.lower()

        if not authorization_header or len(authorization_header) != 2:
            raise exceptions.AuthenticationFailed(
                'Invalid Authorization header format, expecting: JWT <token>.'
            )

        if smart_text(authorization_header[0].lower()) != auth_header_prefix:
            raise exceptions.AuthenticationFailed(
                'Invalid Authorization header prefix, expecting: JWT.'
            )
        
        return authorization_header[1]

    def decode_token(self, firebase_token):
        """
        Attempt to verify JWT from Authorization header with Firebase and
        return the decoded token
        """
        try:
            return firebase_auth.verify_id_token(
                firebase_token,
                check_revoked=api_settings.FIREBASE_CHECK_JWT_REVOKED
            )
        except ValueError as exc:
            raise exceptions.AuthenticationFailed(
                'JWT was found to be invalid, or the App’s project ID cannot '
                'be determined.'
            )
        except (firebase_auth.InvalidIdTokenError, 
                firebase_auth.ExpiredIdTokenError, 
                firebase_auth.RevokedIdTokenError, 
                firebase_auth.CertificateFetchError) as exc:
            if exc.code == 'ID_TOKEN_REVOKED':
                raise exceptions.AuthenticationFailed(
                    'Token revoked, inform the user to reauthenticate or '
                    'signOut().'
                )
            else:
                raise exceptions.AuthenticationFailed(
                    'Token is invalid.'
                )

    def authenticate_token(self, decoded_token):
        """
        Returns firebase user if token is authenticated
        """
        try:
            uid = decoded_token.get('uid')
            firebase_user = firebase_auth.get_user(uid)
            if api_settings.FIREBASE_AUTH_EMAIL_VERIFICATION:
                if not firebase_user.email_verified:
                    raise exceptions.AuthenticationFailed(
                        'Email address of this user has not been verified.'
                    )
            return firebase_user
        except ValueError:
            raise exceptions.AuthenticationFailed(
                'User ID is None, empty or malformed'
            )
        except firebase_auth.AuthError:
            raise exceptions.AuthenticationFailed(
                'Error retrieving the user, or the specified user ID does not '
                'exist'
            )

    def get_or_create_local_user(self, firebase_user):
        """
        Attempts to return or create a local User from Firebase user data
        """
        email = firebase_user.email if firebase_user.email \
            else firebase_user.provider_data[0].email
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                raise exceptions.AuthenticationFailed(
                    'User account is not currently active.'
                )
            user.last_login = timezone.now()
            user.save()
            return user
        except User.DoesNotExist:
            if not api_settings.FIREBASE_CREATE_LOCAL_USER:
                raise exceptions.AuthenticationFailed(
                    'User is not registered to the application.'
                )
            username = '_'.join(
                firebase_user.display_name.split(' ') if firebase_user.display_name \
                else str(uuid.uuid4())
            )
            username = username if len(username) <= 30 else username[:30]
            new_user = User.objects.create_user(
                username=username,
                email=email
            )
            new_user.last_login = timezone.now()
            if api_settings.FIREBASE_ATTEMPT_CREATE_WITH_DISPLAY_NAME:
                display_name = firebase_user.display_name.split()
                if len(display_name) == 2:
                    new_user.first_name = display_name[0]
                    new_user.last_name = display_name[1]
            new_user.save()
            # self.create_local_firebase_user(new_user, firebase_user)
            return new_user

    def create_local_firebase_user(self, user, firebase_user):
        """
        Create a local FireBase model if one does not already exist
        """
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

        # catch locally stored providers that are no longer associated at Firebase
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

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        auth_header_prefix = api_settings.FIREBASE_AUTH_HEADER_PREFIX.lower()
        return '{0} realm="{1}"'.format(auth_header_prefix, self.www_authenticate_realm)
