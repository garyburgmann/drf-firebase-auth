# DRF Firebase Auth

## Requirements


* Python (tested with 3.6)
* Django
* Django Rest Framework



## Installation

```
$ pip install drf-firebase-auth
```

Add the application to your project's `INSTALLED_APPS` in `settings.py`.

```
INSTALLED_APPS = [
    ...
    'drf_firebase_auth',
]
```

In your project's `settings.py`, add this to the `REST_FRAMEWORK` configuration. Note that if you want to retain access to the browsable API for locally created users, then you will probably want to keep `rest_framework.authentication.SessionAuthentication` too.


```
REST_FRAMEWORK = {
  ...
  'DEFAULT_AUTHENTICATION_CLASSES': [
    ...
    'rest_framework.authentication.SessionAuthentication',
    'drf_firebase_auth.authentication.FirebaseAuthentication',
  ]
}
```


The `drf_firebase_auth` application comes with the following settings as default, which can be overridden in your project's `settings.py` file. Make sure to nest them within `DRF_FIREBASE_AUTH` as below:


```
DRF_FIREBASE_AUTH = {
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
```

You can get away with leaving all the settings as default except for `FIREBASE_SERVICE_ACCOUNT_KEY`, which is obviously required. As a minimum, you will need to set this in your project's `settings.py`. This must be the JSON service account key that you receive from the Firebase console for your application.

```
...
DRF_FIREBASE_AUTH = {
    'FIREBASE_SERVICE_ACCOUNT_KEY': 'project/config/firebase.json'
}
```

Now that you have configured the application, make and run the migrations so that the Firebase data can be stored.

```
$ ./manage.py makemigrations drf_firebase_auth
$ ./manage.py migrate drf_firebase_auth
```

## Publishing

`python setup.py sdist`

`twine upload dist/*`
