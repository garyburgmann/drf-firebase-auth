#!/usr/bin/env python3
import os

import setuptools

import drf_firebase_auth as meta

this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name=meta.__title__,
    version=meta.__version__,
    url=meta.__url__,
    license=meta.__license__,
    author=meta.__author__,
    author_email=meta.__author_email__,
    description=meta.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    python_requires='>=3.4',
    install_requires=[
        'djangorestframework>=3.9,<4',
        'firebase-admin>=4.5,<5'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords=[
        'drf',
        'django',
        'rest_framework',
        'djangorestframework',
        'authentication',
        'python3',
        'firebase'
    ],
)
