#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

__author__ = "Fedor Marchenko"
__email__ = "mfs90@mail.ru"
__date__ = "Jul 13, 2016"

import logging
import datetime
from copy import copy

import requests
from requests.auth import HTTPBasicAuth
from requests.compat import urljoin

from django.views.debug import ExceptionReporter
from issues_errors.settings import ISSUE_REPOSITORY_NAME, ISSUE_REPOSITORY_USER, ISSUE_USER_PASSWORD, ISSUE_USER


get_datetime = lambda x: datetime.datetime.strptime(x.get('utc_last_updated')[:-6], '%Y-%m-%d %H:%M:%S')


class BitBucketIssuesHandler(logging.Handler):
    active = True

    def __init__(self, repository_user=None, repository_name=None, user=None, password=None):
        logging.Handler.__init__(self)
        self.repository_user, self.repository_name, self.user, self.password = (
            repository_user or ISSUE_REPOSITORY_USER,
            repository_name or ISSUE_REPOSITORY_NAME,
            user or ISSUE_USER,
            password or ISSUE_USER_PASSWORD
        )
        self.api_url = 'https://api.bitbucket.org/1.0/repositories/%s/%s/' % (
            self.repository_user,
            self.repository_name
        )

        if not (self.repository_user and self.repository_name):
            self.active = False

    def emit(self, record):
        if not self.active:
            return

        try:
            request = record.request
        except Exception:
            request = None

        title = '%s: %s' % (record.exc_info[1].__class__.__name__, record.exc_info[1])
        title = title.replace('\n', '\\n').replace('\r', '\\r')

        issue_id = self.get_issue_id(title)
        if not issue_id:
            no_exc_record = copy(record)
            no_exc_record.exc_info = None
            no_exc_record.exc_text = None

            if record.exc_info:
                exc_info = record.exc_info
            else:
                exc_info = (None, record.getMessage(), None)

            reporter = ExceptionReporter(request, is_email=True, *exc_info)
            message = "%s\n\n%s" % (self.format(no_exc_record), reporter.get_traceback_text())
            self.create_issue(title, message)
        else:
            self.reopen_issue(issue_id)

    def get_issue_id(self, title):
        payload = {'title': title}
        response = requests.get(
            urljoin(self.api_url, 'issues'),
            params=payload,
            auth=HTTPBasicAuth(self.user, self.password)
        ).json()
        if response.get('count', 0) > 0:
            issues = response.get('issues', [])
            issues = sorted(
                issues,
                key=get_datetime,
                reverse=True
            )
            return issues[0].get('local_id', None)
        return None

    def get_issue(self, id):
        return requests.get(
            urljoin(self.api_url, 'issues/%d' % id),
            auth=HTTPBasicAuth(self.user, self.password)
        ).json()

    def create_issue(self, title, content):
        data = {'title': title, 'content': content}
        response = requests.post(
            urljoin(self.api_url, 'issues'),
            data=data,
            auth=HTTPBasicAuth(self.user, self.password)
        ).json()
        return response.get('local_id', None)

    def reopen_issue(self, id, status=2):
        data = {'status': status}
        response = requests.put(
            urljoin(self.api_url, 'issues/%d' % id),
            data=data,
            auth=HTTPBasicAuth(self.user, self.password)
        ).json()
        return response.get('local_id', None)
