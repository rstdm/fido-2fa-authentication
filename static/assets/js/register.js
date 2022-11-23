import * as fidoLayout from "/assets/js/fido-layout.js";
import {
    create,
    parseCreationOptionsFromJSON,
} from '/assets/js/webauthn-json.browser-ponyfill.js';

const authenticateButton = document.getElementById("authenticate-button");

authenticateButton.onclick = onAuthenticateButtonClicked;

function displayFailure() {
    fidoLayout.displayFailure("Registrierung gescheitert");

    authenticateButton.innerText = "Erneut versuchen";
    authenticateButton.style.display = "block";
}

function displayInProgress() {
    fidoLayout.displayInProgress();
    authenticateButton.style.display = "none";
}

async function onAuthenticateButtonClicked() {
    displayInProgress();

    let request = await fetch('/api/register/begin', {
        method: 'POST',
    });
    if (!request.ok) {
        displayFailure();
        let errorMessage = "Failed to retrieve registration data from the server. URL: " + request.url +
            " Status: " + request.status + " Response Body: " + await request.text();
        throw new Error(errorMessage);
    }

    let json = await request.json();
    let options = parseCreationOptionsFromJSON(json);

    let response = null;
    try {
        response = await create(options);
    } catch (e) {
        displayFailure();
        throw Error("The browser could not process the cryptographic challenge. The most likely cause is that the " +
            "user didn't allow the request. Raw Error: " + e)
    }

    let result = await fetch('/api/register/complete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(response),
    });

    if (!result.ok) {
        displayFailure();
        let errorMessage = "The server rejected the signed challenge. URL: " + request.url +
            " Status: " + request.status + " Response Body: " + await request.text();
        throw new Error(errorMessage);
    }

    window.location = "/"
}