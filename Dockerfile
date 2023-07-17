FROM python:3.8-slim

MAINTAINER joshuapy@163.com

ENV TZ=Asia/Shanghai

WORKDIR /app

COPY . /app

RUN pip install -U pip && pip --no-cache-dir install -r requirements.txt

CMD ["sh", "-c", "python main.py"]
