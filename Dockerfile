FROM python:slim-bullseye
RUN mkdir /scan
COPY . /scan
RUN pip install /scan/42ctl-0.1.4-py3-none-any.whl
