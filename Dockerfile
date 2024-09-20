FROM python:3.8-slim

MAINTAINER joshuapy@163.com

ENV TZ=Asia/Shanghai

WORKDIR /app

COPY . /app

RUN pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ && pip --no-cache-dir install  -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

CMD ["sh", "-c", "python main.py"]
