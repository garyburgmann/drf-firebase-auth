# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FirebaseUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=191)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='firebase_user', related_query_name='firebase_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FirebaseUserProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=191)),
                ('provider_id', models.CharField(max_length=50)),
                ('firebase_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provider', related_query_name='provider', to='drf_firebase_auth.FirebaseUser')),
            ],
        ),
    ]

