#!/usr/bin/sh
set -e

mkdir -p certs

echo "Creating self signed certificate"
openssl req -newkey rsa:4096  -x509  -sha512  -days 365 -nodes -out certs/certificate.pem -keyout certs/privatekey.pem -batch

echo "starting server"
gunicorn server:app --access-logfile=- --bind 0.0.0.0:8000 --certfile=certs/certificate.pem --keyfile=certs/privatekey.pem

# TODO change user