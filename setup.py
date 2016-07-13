import os
from setuptools import setup

install_requires = []
install_requires.extend(open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
).read().split())

setup(
    name='django-issues-errors',
    version='0.1.0',
    description='Special python logging handler for send errors to bitbucket.org',
    long_description=open('README.md').read(),
    license='MIT License',
    author='Fedor Marchenko',
    author_email='mfs90@mail.ru',
    url='https://bitbucket.org/fmarchenko/bitbucket-issues/',
    zip_safe=False,
    packages=['issues_errors'],
    platforms='any',
    install_requires=install_requires,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 1 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Django',
        'Topic :: Logging',
        'Topic :: Utilities'
        ],
    keywords='',
)
