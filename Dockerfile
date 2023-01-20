FROM python:3.11-slim
WORKDIR /app

# the code in the container shouldn't run as root
RUN groupadd -r pythonuser && useradd -r -g pythonuser pythonuser

# allow the pythonuser to store certificates and the database
RUN mkdir -p certs \
    && chmod -R a+rw certs \
    && mkdir -p database \
    && chmod -R a+rw database

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# todo dockerignore (internal oder src ordner?), volume
COPY server.py docker_launch.sh ./
COPY app/ app/
COPY templates/ templates/
COPY static/ static/

USER pythonuser
CMD ["/bin/sh", "docker_launch.sh"]

