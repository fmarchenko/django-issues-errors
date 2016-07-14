#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

__author__ = "Fedor Marchenko"
__email__ = "mfs90@mail.ru"
__date__ = "Jul 13, 2016"

import logging
import datetime
import json
from copy import copy

import requests
from requests.auth import HTTPBasicAuth
from requests.compat import urljoin

from django.views.debug import ExceptionReporter
from issues_errors.settings import ISSUE_REPOSITORY_NAME, ISSUE_REPOSITORY_USER, ISSUE_USER_PASSWORD, ISSUE_USER


def get_datetime(date_str, format_str='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(date_str, format_str)


class BaseIssuesHandler(logging.Handler):
    active = True
    api_url_template = '/%s/%s/'

    def __init__(self, repository_user=None, repository_name=None, user=None, password=None):
        logging.Handler.__init__(self)
        self.repository_user, self.repository_name, self.user, self.password = (
            repository_user or ISSUE_REPOSITORY_USER,
            repository_name or ISSUE_REPOSITORY_NAME,
            user or ISSUE_USER,
            password or ISSUE_USER_PASSWORD
        )

        self.generate_api_url()

        if not (self.repository_user and self.repository_name):
            self.active = False

    def generate_api_url(self):
        self.api_url = self.api_url_template % (
            self.repository_user,
            self.repository_name
        )

    def add_auth(self, kwargs):
        if self.user and self.password:
            kwargs['auth'] = HTTPBasicAuth(self.user, self.password)
        return kwargs

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
        print('TODO get_issue_id')

    def get_issue(self, id):
        print('TODO get_issue')

    def create_issue(self, title, content):
        print('TODO create_issue')

    def reopen_issue(self, id, status=2):
        print('TODO reopen_issue')


class BitBucketIssuesHandler(BaseIssuesHandler):
    api_url_template = 'https://api.bitbucket.org/1.0/repositories/%s/%s/'

    def get_issue_id(self, title):
        payload = {'title': title}
        kwargs = {
            'url': urljoin(self.api_url, 'issues'),
            'params': payload,
        }
        kwargs = self.add_auth(kwargs)
        response = requests.get(**kwargs).json()
        if response.get('count', 0) > 0:
            issues = response.get('issues', [])
            issues = sorted(
                issues,
                key=lambda x: get_datetime(x.get('utc_last_updated')[:-6]),
                reverse=True
            )
            return issues[0].get('local_id', None)
        return None

    def get_issue(self, id):
        kwargs = {'url': urljoin(self.api_url, 'issues/%d' % id)}
        kwargs = self.add_auth(kwargs)
        return requests.get(**kwargs).json()

    def create_issue(self, title, content):
        data = {'title': title, 'content': content}
        kwargs = {'url': urljoin(self.api_url, 'issues'), 'data': data}
        kwargs = self.add_auth(kwargs)
        response = requests.post(**kwargs).json()
        return response.get('local_id', None)

    def reopen_issue(self, id, status=2):
        data = {'status': status}
        kwargs = {'url': urljoin(self.api_url, 'issues/%d' % id), 'data': data}
        kwargs = self.add_auth(kwargs)
        response = requests.put(**kwargs).json()
        return response.get('local_id', None)


class GitHubIssuesHandler(BaseIssuesHandler):
    api_url_template = 'https://api.github.com/'

    def generate_api_url(self):
        self.api_url = self.api_url_template

    def get_issue_id(self, title):
        payload = {'q': '%s in:title repo:%s/%s' % (title, self.repository_user, self.repository_name)}
        kwargs = {
            'url': urljoin(self.api_url, 'search/issues'),
            'params': payload,
        }
        kwargs = self.add_auth(kwargs)
        response = requests.get(**kwargs).json()
        if response.get('total_count', 0) > 0:
            issues = response.get('items', [])
            issues = sorted(
                issues,
                key=lambda x: get_datetime(x.get('created_at'), '%Y-%m-%dT%H:%M:%SZ'),
                reverse=True
            )
            return issues[0].get('number', None)
        return None

    def create_issue(self, title, content):
        data = {'title': title, 'body': content, 'labels': ['bug']}
        kwargs = {
            'url': urljoin(self.api_url, 'repos/%s/%s/issues' % (self.repository_user, self.repository_name)),
            'data': json.dumps(data)
        }
        kwargs = self.add_auth(kwargs)
        response = requests.post(**kwargs).json()
        return response.get('number', None)

    def reopen_issue(self, id, status='open'):
        data = {'state': status}
        kwargs = {
            'url': urljoin(self.api_url, 'repos/%s/%s/issues/%d' % (self.repository_user, self.repository_name, id)),
            'data': json.dumps(data)
        }
        kwargs = self.add_auth(kwargs)
        response = requests.patch(**kwargs).json()
        return response.get('number', None)
