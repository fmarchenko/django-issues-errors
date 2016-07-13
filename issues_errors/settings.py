#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

__author__ = "Fedor Marchenko"
__email__ = "mfs90@mail.ru"
__date__ = "Jul 13, 2016"

from django.conf import settings

ISSUE_REPOSITORY_USER = getattr(settings, 'ISSUE_REPOSITORY_USER', None)
ISSUE_REPOSITORY_NAME = getattr(settings, 'ISSUE_REPOSITORY_NAME', None)
ISSUE_USER = getattr(settings, 'ISSUE_USER', None)
ISSUE_USER_PASSWORD = getattr(settings, 'ISSUE_USER_PASSWORD', None)
