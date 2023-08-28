FROM python:slim-bullseye
RUN mkdir /scan
COPY . /scan
RUN pip install /scan/42c_cli-0.1.2-py3-none-any.whl