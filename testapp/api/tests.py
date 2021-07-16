from unittest import mock

from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
import requests
import firebase_admin
from firebase_admin import auth as firebase_auth
from drf_firebase_auth.settings import api_settings
from drf_firebase_auth.utils import (
    get_firebase_user_identifier,
    map_firebase_uid_to_username,
    map_firebase_email_to_username
)

User = get_user_model()
firebase_credentials = firebase_admin.credentials.Certificate(
    api_settings.FIREBASE_SERVICE_ACCOUNT_KEY
)
firebase = firebase_admin.initialize_app(
    credential=firebase_credentials,
    name=__name__
)

class WhoAmITests(APITestCase):

    def setUp(self):
        self._url = reverse('whoami')
        self._test_user_email = 'user@example.com'
        self._id_token_endpoint = (
            'https://identitytoolkit.googleapis.com/v1/accounts'
            ':signInWithCustomToken?key={api_key}'
        )
        self._MOCK_FIREBASE_CREATE_LOCAL_USER_FALSE = mock.patch(
            'drf_firebase_auth.authentication.api_settings'
            '.FIREBASE_CREATE_LOCAL_USER',
            new=False
        )
        self._MOCK_FIREBASE_CREATE_LOCAL_USER_TRUE = mock.patch(
            'drf_firebase_auth.authentication.api_settings'
            '.FIREBASE_CREATE_LOCAL_USER',
            new=True
        )
        self._MOCK_FIREBASE_USERNAME_MAPPING_FUNC_UID = mock.patch(
            'drf_firebase_auth.authentication.api_settings'
            '.FIREBASE_USERNAME_MAPPING_FUNC',
            new=map_firebase_uid_to_username
        )
        self._MOCK_FIREBASE_USERNAME_MAPPING_FUNC_EMAIL = mock.patch(
            'drf_firebase_auth.authentication.api_settings'
            '.FIREBASE_USERNAME_MAPPING_FUNC',
            new=map_firebase_email_to_username
        )

    def _get_test_user(self) -> firebase_admin.auth.UserRecord:
        try:
            return firebase_auth.get_user_by_email(self._test_user_email)
        except Exception as e:
            raise Exception(e)

    def _create_custom_token(self) -> str:
        try:
            user = self._get_test_user()
            return firebase_admin.auth.create_custom_token(user.uid)
        except Exception as e:
            raise Exception(e)

    def _generate_id_token(self) -> str:
        """
        generate an id token for testing against api

        https://firebase.google.com/docs/reference/rest/auth/
        """
        try:
            url = self._id_token_endpoint.format(
                api_key=settings.FIREBASE_DRF_FIREBASE_AUTH_API_KEY
            )
            data = {
                'token': self._create_custom_token(),
                'returnSecureToken': True
            }
            res = requests.post(url, data=data)
            res.raise_for_status()
            return res.json()['idToken']
        except Exception as e:
            raise Exception(e)

    def test_authenticated_request(self):
        """ ensure we can auth with a valid id token """
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f'{api_settings.FIREBASE_AUTH_HEADER_PREFIX} '
                f'{self._generate_id_token()}'
            )
        )

        with self._MOCK_FIREBASE_CREATE_LOCAL_USER_FALSE:
            response = self.client.get(self._url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f'{api_settings.FIREBASE_CREATE_LOCAL_USER}'
            )

        with self._MOCK_FIREBASE_CREATE_LOCAL_USER_TRUE:
            response = self.client.get(self._url)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f'{response.data}'
            )

            expected_user = self._get_test_user()
            self.assertTrue('request.auth' in response.data)
            self.assertEqual(response.data['request.auth']['uid'], expected_user.uid)

    def test_unauthenticated_request(self):
        """ ensure we cannot auth without a valid id token """
        response = self.client.get(self._url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_token_request(self):
        """ ensure we cannot auth with an invalid id token """
        # verify_id_token should raise on custom token
        invalid_token = self._create_custom_token()
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f'{api_settings.FIREBASE_AUTH_HEADER_PREFIX} '
                f'{invalid_token}'
            )
        )
        response = self.client.get(self._url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_creation_uid_as_username(self):
        """ ensure user is created dependent on FIREBASE_CREATE_LOCAL_USER """
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f'{api_settings.FIREBASE_AUTH_HEADER_PREFIX} '
                f'{self._generate_id_token()}'
            )
        )
        firebase_user = self._get_test_user()
        firebase_user_email = get_firebase_user_identifier(firebase_user)

        with self._MOCK_FIREBASE_CREATE_LOCAL_USER_FALSE:
            before_count = User.objects.count()

            response = self.client.get(self._url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f'{response.data}'
            )

            after_count = User.objects.count()
            expected_count = before_count
            self.assertEqual(expected_count, after_count)

            with self.assertRaises(Exception):
                _ = User.objects.get(email=firebase_user_email)

        with self._MOCK_FIREBASE_CREATE_LOCAL_USER_TRUE:
            with self._MOCK_FIREBASE_USERNAME_MAPPING_FUNC_UID:
                before_count = User.objects.count()

                response = self.client.get(self._url)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    f'{response.data}'
                )

                after_count = User.objects.count()
                expected_count = before_count + 1
                self.assertEqual(expected_count, after_count)

                self.assertIsNotNone(
                    User.objects.filter(email=firebase_user_email).first()
                )
                self.assertIsNotNone(
                    User.objects.filter(username=firebase_user.uid).first()
                )

    def test_user_creation_email_as_username(self):
        """ ensure user is created dependent on FIREBASE_CREATE_LOCAL_USER """
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f'{api_settings.FIREBASE_AUTH_HEADER_PREFIX} '
                f'{self._generate_id_token()}'
            )
        )
        firebase_user = self._get_test_user()
        firebase_user_email = get_firebase_user_identifier(firebase_user)

        with self._MOCK_FIREBASE_CREATE_LOCAL_USER_FALSE:
            before_count = User.objects.count()

            response = self.client.get(self._url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f'{response.data}'
            )

            after_count = User.objects.count()
            expected_count = before_count
            self.assertEqual(expected_count, after_count)

            with self.assertRaises(Exception):
                _ = User.objects.get(email=firebase_user_email)

        with self._MOCK_FIREBASE_CREATE_LOCAL_USER_TRUE:
            with self._MOCK_FIREBASE_USERNAME_MAPPING_FUNC_EMAIL:
                before_count = User.objects.count()

                response = self.client.get(self._url)
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    f'{response.data}'
                )

                after_count = User.objects.count()
                expected_count = before_count + 1
                self.assertEqual(expected_count, after_count)

                self.assertIsNotNone(
                    User.objects.filter(email=firebase_user_email).first()
                )
                self.assertIsNotNone(
                    User.objects.filter(username=firebase_user_email).first()
                )
