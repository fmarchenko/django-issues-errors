# Django Issues

Special python logging handler for send errors to bitbucket.org

### Version
0.1.1

### Installation

For installation you need run command:

```sh
$ python setup.py
```

### Requirements
```sh
Django>=1.5
requests==2.10.0
```

### Settings example
```sh
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'issues': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'issues_errors.log.BitBucketIssuesHandler', # or 'class': 'issues_errors.log.GitHubIssuesHandler' if use github.com issues
            'repository_user': 'owner_repository_user',
            'repository_name': 'repository_name',
            'user': 'username_for_create_issue',
            'password': 'user_password_for_create_issue'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'django.request': {
            'handlers': ['mail_admins', 'issues'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
    }
}
```

### Todos

 - Write Tests

License
----

MIT

### Author

Fedor Marchenko

**Free Software, Hell Yeah!**
