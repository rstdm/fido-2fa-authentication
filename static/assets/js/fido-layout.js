
const inProgressDiv = document.getElementById("fido-layout-inprogress-div");
const failedAlert = document.getElementById("fido-layout-failed-alert");
const failedAlertMessage = document.getElementById("fido-layout-failed-alert-message");

export function displayFailure(message) {
    failedAlertMessage.innerText = message;
    failedAlert.classList.remove("d-none");

    inProgressDiv.classList.add("d-none");
}

export function displayInProgress() {
    failedAlert.classList.add("d-none");
    inProgressDiv.classList.remove("d-none");
}