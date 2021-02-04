# DRF Firebase Auth

## Requirements


* Python3
* Django
* Django Rest Framework



## Installation

```
$ pip install drf-firebase-auth
```

Add the application to your project's `INSTALLED_APPS` in `settings.py`.

```python
INSTALLED_APPS = [
    ...
    'drf_firebase_auth',
]
```

In your project's `settings.py`, add this to the `REST_FRAMEWORK` configuration. Note that if you want to retain access to the browsable API for locally created users, then you will probably want to keep `rest_framework.authentication.SessionAuthentication` too.


```python
REST_FRAMEWORK = {
  ...
  'DEFAULT_AUTHENTICATION_CLASSES': [
    ...
    'rest_framework.authentication.SessionAuthentication',
    'drf_firebase_auth.authentication.FirebaseAuthentication',
  ]
}
```


The `drf_firebase_auth` application comes with the following settings as default, which can be overridden in your project's `settings.py` file. For convenience in version >= 1, most of these can be conveniently set form environment variables also. Make sure to nest them within `DRF_FIREBASE_AUTH` as below:


```python
DRF_FIREBASE_AUTH = {
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
    'FIREBASE_USERNAME_MAPPING_FUNC': map_firebase_uid_to_username
}
```

You can get away with leaving all the settings as default except for `FIREBASE_SERVICE_ACCOUNT_KEY`, which is obviously required.

NOTE: `FIREBASE_USERNAME_MAPPING_FUNC` will replace behaviour in version < 1 as default (formerly provided by logic in `map_firebase_to_username_legacy`, described below). One can simply switch out this function.

`drf_firebase_auth.utils` contains functions for mapping firebase user info to the Django username field (new in version >= 1). Any custom function can be supplied here, as long as it accepts a `firebase_admin.auth.UserRecord` argument. The supplied functions are common use-cases:

```python
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
```

Now that you have configured the application, run the migrations so that the Firebase data can be stored.

```
$ ./manage.py migrate drf_firebase_auth
```

All you need to do now is have your client code handle the Firebase popup/redirect authentication flow, retrieve the idToken from the currentUser (Firebase explains this flow well in their docs: `https://firebase.google.com/docs/auth/admin/verify-id-tokens`), and then use the idToken for the user in an `Authorization` header in requests to your API.

```
JWT <token>
```

Voila!

## Contributing

* Trello board created! Please follow this link if you wish to collabrate in the future direction of this package: https://trello.com/invite/b/lkAsvStS/af54d9a94359c042f3bd9afb47f82eab/drf-firebase-auth
* Please raise an issue/feature and name your branch 'feature-n' or 'issue-n', where 'n' is the issue number.
* If you test this code with a Python version not listed above and all is well, please fork and update the README to include the Python version you used :)
* I almost always setup Django with a custom user class inheriting from AbstractUser, where I switch the USERNAME_FIELD to be 'email'. This backend is setup to assign a username still anyway, but if there are any issues, please raise them and/or make a pull request to help the community!
