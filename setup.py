from setuptools import find_packages, setup
from os import path

NAME = 'drapps'
REPO_NAME = 'dr-streamlit'


install_requires = [
    'bson==0.5.10',
    'click==8.1.7',
    'requests==2.31.0',
]

setup(
    name=NAME,
    description='CLI client for custom application in Data Robot',
    long_description=open(path.join(path.dirname(__file__), 'README.md')).read(),
    author='Data Robot',
    url='https://github.com/datarobot/{}'.format(REPO_NAME),
    version='0.1.0',
    packages=find_packages(include=[NAME]),
    package_dir={NAME: NAME},
    python_requires='>=3.7',
    install_requires=install_requires,
    scripts=[path.join(NAME, 'drapps.py')],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
    ],
)