#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

import dj_email_url
import django

# Setup Django environment
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_test_settings')
django.setup()


class EmailTestSuite(unittest.TestCase):
    def test_smtp_parsing(self):
        url = 'smtps://user@domain.com:password@smtp.example.com:587'
        url = dj_email_url.parse(url)

        assert url['EMAIL_BACKEND'] == \
            'django.core.mail.backends.smtp.EmailBackend'
        assert url['EMAIL_HOST'] == 'smtp.example.com'
        assert url['EMAIL_HOST_PASSWORD'] == 'password'
        assert url['EMAIL_HOST_USER'] == 'user@domain.com'
        assert url['EMAIL_PORT'] == 587
        assert url['EMAIL_USE_TLS'] is True

    def test_email_url(self):
        a = dj_email_url.config()
        assert not a

        os.environ['EMAIL_URL'] = \
            'smtps://user@domain.com:password@smtp.example.com:587'

        url = dj_email_url.config()

        assert url['EMAIL_BACKEND'] == \
            'django.core.mail.backends.smtp.EmailBackend'
        assert url['EMAIL_HOST'] == 'smtp.example.com'
        assert url['EMAIL_HOST_PASSWORD'] == 'password'
        assert url['EMAIL_HOST_USER'] == 'user@domain.com'
        assert url['EMAIL_PORT'] == 587
        assert url['EMAIL_USE_TLS'] is True

    def test_smtp_backend_with_ssl(self):
        url = 'smtp://user@domain.com:pass@smtp.example.com:465/?ssl=True'
        url = dj_email_url.parse(url)
        assert url['EMAIL_USE_SSL'] is True
        assert url['EMAIL_USE_TLS'] is False

    def test_smtp_backend_with_tls(self):
        url = 'smtp://user@domain.com:pass@smtp.example.com:587/?tls=True'
        url = dj_email_url.parse(url)
        assert url['EMAIL_USE_SSL'] is False
        assert url['EMAIL_USE_TLS'] is True


class DjangoSettingsTestSuite(unittest.TestCase):

    def test_settings(self):
        from django.conf import settings
        conf = dj_email_url.parse(settings.EMAIL_URL)
        for key, value in conf.items():
            self.assertEqual(getattr(settings, key), conf[key])


if __name__ == '__main__':
    unittest.main()
