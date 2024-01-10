from os import path

from setuptools import find_packages, setup

NAME = 'drapps'
REPO_NAME = 'dr-apps'


install_requires = [
    'bson==0.5.10',
    'click==8.1.7',
    'requests==2.31.0',
]

tests_require = [
    'pytest==7.4.3',
    'responses==0.23.3',
    'black==23.12.0 ',
    'flake8==6.1.0',
    'mypy==1.7.1',
    'types-requests==2.31.0.10',
    'isort==5.13.2',
]

setup(
    name=NAME,
    description='CLI client for custom application in Data Robot',
    long_description=open(path.join(path.dirname(__file__), 'README.md')).read(),
    author='Data Robot',
    url='https://github.com/datarobot/{}'.format(REPO_NAME),
    packages=find_packages(exclude=['examples']),
    package_dir={NAME: NAME},
    python_requires='>=3.7',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    scripts=['bin/drapps'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        'Operating System :: OS Independent',
    ],
)
