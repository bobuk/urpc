FROM python:alpine
MAINTAINER Grigory Bakunov <thebobuk@ya.ru>

RUN pip install --upgrade pip
RUN pip install defaultenv redis urpc
