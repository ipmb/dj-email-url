# -*- coding: utf-8 -*-

import logging
import os
from django.apps import AppConfig
from django.conf import settings, global_settings, UserSettingsHolder

logger = logging.getLogger(__name__)

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

default_app_config = 'dj_email_url.DjEmailUrlConfig'

class DjEmailUrlConfig(AppConfig):
    name = 'dj_email_url'

    def _is_default_setting(self, key):
        return (getattr(settings, key, None) ==
                getattr(global_settings, key, None))

    def ready(self):
        """Overwrite EMAIL_* settings based on settings.EMAIL_URL"""
        email_url = getattr(settings, 'EMAIL_URL', None)
        if not email_url:
            return
        conf = parse(email_url)
        new_settings = UserSettingsHolder(settings._wrapped)
        for key, value in conf.items():
            if not self._is_default_setting(key):
                logger.warn('dj-email-url is overridding settings.%s', key)
            setattr(new_settings, key, value)
        settings._wrapped = new_settings


# Register email schemes in URLs.
urlparse.uses_netloc.append('smtp')
urlparse.uses_netloc.append('console')
urlparse.uses_netloc.append('file')
urlparse.uses_netloc.append('memory')
urlparse.uses_netloc.append('dummy')


DEFAULT_ENV = 'EMAIL_URL'


SCHEMES = {
    'smtp': 'django.core.mail.backends.smtp.EmailBackend',
    'smtps': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
    'file': 'django.core.mail.backends.filebased.EmailBackend',
    'memory': 'django.core.mail.backends.locmem.EmailBackend',
    'dummy': 'django.core.mail.backends.dummy.EmailBackend'
}


def config(env=DEFAULT_ENV, default=None):
    """Returns a dictionary with EMAIL_* settings from EMAIL_URL."""

    conf = {}

    s = os.environ.get(env, default)

    if s:
        conf = parse(s)

    return conf


def parse(url):
    """Parses an email URL."""

    conf = {}

    url = urlparse.urlparse(url)

    # Remove query strings
    path = url.path[1:]
    path = path.split('?', 2)[0]

    # Update with environment configuration
    conf.update({
        'EMAIL_FILE_PATH': path,
        'EMAIL_HOST_USER': url.username,
        'EMAIL_HOST_PASSWORD': url.password,
        'EMAIL_HOST': url.hostname,
        'EMAIL_PORT': url.port,
    })

    if url.scheme in SCHEMES:
        conf['EMAIL_BACKEND'] = SCHEMES[url.scheme]

    if url.scheme == 'smtps':
        conf['EMAIL_USE_TLS'] = True
    else:
        conf['EMAIL_USE_TLS'] = False

    if url.scheme == 'smtp':
        qs = urlparse.parse_qs(url.query)
        if 'ssl' in qs and qs['ssl']:
            if qs['ssl'][0] in ('1', 'true', 'True'):
                conf['EMAIL_USE_SSL'] = True
                conf['EMAIL_USE_TLS'] = False
        if 'tls' in qs and qs['tls']:
            if qs['tls'][0] in ('1', 'true', 'True'):
                conf['EMAIL_USE_SSL'] = False
                conf['EMAIL_USE_TLS'] = True

    return conf
