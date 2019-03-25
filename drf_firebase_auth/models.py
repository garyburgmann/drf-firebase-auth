# -*- coding: utf-8 -*-
"""
Models for storing the uid of authenticating firebase users and relating them
to the local AUTH_USER_MODEL model.
Author: Gary Burgmann
Email: garyburgmann@gmail.com
Location: Springfield QLD, Australia
Last update: 2019-02-10
"""
from django.db import models
from django.conf import settings


class FirebaseUser(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        related_name='firebase_user',
        related_query_name='firebase_user',
    )
    uid = models.CharField(max_length=191, null=False,)


class FirebaseUserProvider(models.Model):
    firebase_user = models.ForeignKey(
        'FirebaseUser',
        on_delete=models.CASCADE,
        null=False,
        related_name='provider',
        related_query_name='provider',
    )
    uid = models.CharField(max_length=191, null=False,)
    provider_id = models.CharField(max_length=50, null=False,)
