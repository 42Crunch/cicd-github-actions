FROM python:slim-bullseye
RUN mkdir /scan
COPY . /scan
RUN pip install /scan/*.whl