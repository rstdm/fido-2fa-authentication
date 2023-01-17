# fido-deliverable
This project is part of the Module 'Sicherheit und Webanwendungen' at the University of Applied Sciences in Lübeck.

It was the goal, to demonstrate the usage of the FIDO2 protocol in a web application and to implement a FIDO2 server.
You can register and authenticate with a FIDO2 device (from Yubikey). Your registert device will be stored in a persistent database.
Beware that the FIDO2 server is not production ready and should not be used in a production environment.


## Run local
To run this project locally, is is nessessary to install all requirements and run the following command:

    pip3 install -r requirements.txt
    python3 server.py

## Run with docker
It is possible, to run this project in a docker container. To do so, you need to install docker. Then you can run the following commands:

    docker build -t fido:1.0 .
    docker run -p5000:5000 fido:1.0
