FROM python:3.10

WORKDIR /opt/workspace/
COPY setup.py setup.cfg Makefile .flake8 mypy.ini pyproject.toml ./
RUN mkdir firebat
RUN make req-test

