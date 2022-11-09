FROM python:3.11-slim

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

ADD . /app
WORKDIR /app

CMD ["python3", "server.py"]

