from os import path

from setuptools import find_packages, setup

NAME = 'drapps'
REPO_NAME = 'dr-apps'


install_requires = [
    'bson==0.5.10',
    'click==8.1.7',
    'dateutils==0.6.12',
    'requests>=2.28,<2.29',
    'requests-toolbelt==1.0.0',
    'tabulate==0.9.0',
]

tests_require = [
    'pytest==7.4.3',
    'responses==0.23.1',
    'black==23.12.0',
    'flake8==6.1.0',
    'isort==5.13.2',
    'mypy==1.7.1',
    'types-requests==2.28.11',
    'types-tabulate==0.9.0.20240106',
    'types-python-dateutil==2.8.19.20240106',
    'streamlit==1.40.0',
    'datarobot==3.5.2',
    'plotly==5.24.1',
    'kaleido==0.2.1',
    'tabulate==0.9.0',
    'altair==5.4.1',
    'pillow==11.0.0',
    'wordcloud>=1.9.4',
]

setup(
    name=NAME,
    description='CLI client for custom application in Data Robot',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Data Robot',
    url='https://github.com/datarobot/{}'.format(REPO_NAME),
    packages=find_packages(exclude=['examples']),
    package_dir={NAME: NAME},
    python_requires='>=3.9',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    scripts=['bin/drapps'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        'Operating System :: OS Independent',
    ],
)
