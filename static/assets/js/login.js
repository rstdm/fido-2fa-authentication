import * as fidoLayout from "/assets/js/fido-layout.js";
import {
    get,
    parseRequestOptionsFromJSON,
} from '/assets/js/webauthn-json.browser-ponyfill.js';

const authenticateButton = document.getElementById("authenticate-button");

authenticateButton.onclick = onAuthenticateButtonClicked

function displayFailure() {
    fidoLayout.displayFailure("Anmeldung gescheitert");

    authenticateButton.innerText = "Erneut versuchen";
    authenticateButton.classList.remove("d-none");
}

function displayInProgress() {
    fidoLayout.displayInProgress();
    authenticateButton.classList.add("d-none");
}

async function onAuthenticateButtonClicked() {
    displayInProgress();

    let request = await fetch('/api/authenticate/begin', {
        method: 'POST',
    });
    if (!request.ok) {
        displayFailure();
        let errorMessage = "Failed to retrieve authentication data from the server. URL: " + request.url +
            " Status: " + request.status + " Response Body: " + await request.text();
        throw new Error(errorMessage);
    }
    let json = await request.json();
    let options = parseRequestOptionsFromJSON(json);

    let response = null;
    try {
        response = await get(options);
    } catch (e) {
        displayFailure();
        throw Error("The browser could not process the cryptographic challenge. The most likely cause is that the " +
            "user didn't allow the request. Raw Error: " + e)
    }

    let result = await fetch('/api/authenticate/complete', {
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