# fido-deliverable
This project was created during the course 'Sicherheit und Webanwendungen' at the University of Applied Sciences in Lübeck.

This project demonstrates the usage of the FIDO2 protocol to secure a web application.
Users can create a new account and authenticate using their chosen username and password. Users can also enable FIDO as an optional second factor.

All data is persisted in a lightweight database. Only salted password hashes are saved.

## List of Features

- Create an account using username and password
- Login with username and password
- Register a FIDO2 device
- Authenticate with username and password (first factor) and FIDO (second factor)

This application was designed with strong security considerations in mind. It's not vulnerable to XSS,
CORS, CSRF, Clickjacking and SQL-Injections.

## Hosting the application

For security reasons browsers only allow the usage of FIDO on webpages that are transmitted using HTTPS. The browser ensures that the certificate is valid (e.g. not expired, webpage domain is identical to certificate domain, etc.) and prevents the usage of FIDO otherwise.

To host the application on your own you therefore have to use a valid certificate. The application currently generates a self-signed certificate at runtime.

Due to the self-signed certificate the usage of FIDO isn't possible if the application is used via a domain or an IP-address. However, most browsers treat `localhost` specially and allow the usage of FIDO if the webpage is retrieved from `localhost`.

## Run locally
To run this project locally, it is necessary to install all requirements. Execute these commands to do so:

    pip3 install -r requirements.txt
    python3 server.py

The application is then available on **https://localhost:5000**. Note that the browser blocks FIDO for any other host (e.g. 127.0.0.1) due to the security restrictions that were mentioned in the section before.

The server stores its database in the `database` folder.

## Run with docker
It is possible to run this project in a docker container. To do so, you need to install docker. Then you can execute the following commands:

    docker build -t fido:1.0 .
    docker run -ti -p 8000:8000 fido:1.0

The application is available on **https://localhost:8000**. Note that the usage of HTTP**S** is mandatory; the server doesn't respond to HTTP requests.

The previous example stores the database in the container. Execute this snippet on a UNIX-like system (macOS, Linux), if you want to create the database on your disk:

    mkdir database
    chmod -R a+rwx database
    docker run -ti -p 8000:8000 --mount type=bind,source="$(pwd)/database2",target=/app/database fido:1.0
