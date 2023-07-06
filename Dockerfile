FROM python:3.12-rc-bookworm
COPY ./ /scanBuild/dist/*.whl /scan/
RUN pip install scan/*.whl