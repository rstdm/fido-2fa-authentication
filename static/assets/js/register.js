import * as fidoLayout from "/assets/js/fido-layout.js";
import {
    create,
    parseCreationOptionsFromJSON,
} from '/assets/js/webauthn-json.browser-ponyfill.js';

const buttonDiv = document.getElementById("button-div");
const textNoPlatformSupport = document.getElementById("text-no-platform-support");
const textPlatformSupport = document.getElementById("text-platform-support");
const authenticateButton = document.getElementById("authenticate-button");

const radioDiv = document.getElementById("radio-div");
const platformRadio = document.getElementById("platform-radio");
const crossPlatformRadio = document.getElementById("cross-platform-radio");

authenticateButton.onclick = onAuthenticateButtonClicked;

checkPlatformSupport();

async function checkPlatformSupport() {
    let platformSupportsFido = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    if (platformSupportsFido) {
        textNoPlatformSupport.classList.add("d-none");
        textPlatformSupport.classList.remove("d-none");
        radioDiv.classList.remove("d-none");

        if (platformRadio.checked || crossPlatformRadio.checked) {
            return
        }

        authenticateButton.disabled = true;
        platformRadio.oninput = (e => {
            authenticateButton.disabled = false;
        })
        crossPlatformRadio.oninput = (e => {
            authenticateButton.disabled = false;
        })
    }
}

function displayFailure() {
    fidoLayout.displayFailure("Einrichten von FIDO gescheitert");

    authenticateButton.innerText = "Erneut versuchen";
    buttonDiv.style.display = "block";
}

function displayInProgress() {
    fidoLayout.displayInProgress();
    buttonDiv.style.display = "none";
}

async function onAuthenticateButtonClicked() {
    displayInProgress();

    let platformSupportsFido = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    let useCrossPlatform = !platformSupportsFido || crossPlatformRadio.checked

    let request = await fetch('/api/register/begin', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'crossPlatform': useCrossPlatform})
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