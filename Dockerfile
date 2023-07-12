FROM python:3.11-slim

MAINTAINER joshuapy@163.com

WORKDIR /app

COPY . /app

RUN pip install -U pip && pip install -r requirements.txt


CMD ['python' 'main.py']
