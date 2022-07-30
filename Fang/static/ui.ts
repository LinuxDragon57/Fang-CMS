function hideFlashedMessages() {
    let previousScrollPosition = window.scrollY;

    window.onscroll = function() {
        let currentScrollPosition = window.scrollY;
        if (previousScrollPosition > currentScrollPosition) {
            document.getElementById("flashedMessage").style.top = "0";
        } else {
            document.getElementById("flashedMessage").style.top = "-128px";
        }
        previousScrollPosition = currentScrollPosition;
    }
}


function getCurrentYear() {
    return new Date().getFullYear().toString();
}

function displayHttpResponse() {
    let errorMsg: string;
    let httpCode: string;
    const HttpStatus = new XMLHttpRequest().status;
    document.getElementById("httpResponse").innerHTML = HttpStatus.toString();
    switch(HttpStatus) {
        case 401:
            errorMsg = "You are not authorized to access the requested resource on this server.";
            httpCode = 'UNAUTHORIZED';
            break;
        case 403:
            errorMsg = "You do not have privileges to access this particular resource.";
            httpCode = 'FORBIDDEN';
            break;
        case 404:
            errorMsg = "You tried to access a resource that couldn't be found.";
            httpCode = 'PAGE NOT FOUND';
            break;
        case 405:
            errorMsg = "You tried to access a server resource in an unauthorized manner.";
            httpCode = 'METHOD NOT ALLOWED';
            break;
        case 408:
            errorMsg = "Unfortunately, the request handshake took too long to execute.";
            httpCode = 'REQUEST TIMEOUT';
            break;
        case 502:
            errorMsg = "The server has a malformed configuration that halted the request.";
            httpCode = 'BAD GATEWAY';
            break;
        case 503:
            errorMsg = "The server went down and was unable to complete your request.";
            httpCode = 'SERVICE UNAVAILABLE';
            break;
        case 504:
            errorMsg = "The server couldn't find the resource."
            httpCode = 'GATEWAY TIMEOUT';
            break;
        default:
            // Will probably never execute. Hopefully...
            errorMsg = "Supposedly, there is an error. However, it has been handled incorrectly.";
            httpCode = 'UNKNOWN ERROR';
    }
    if (HttpStatus !== 400 && HttpStatus !== 500) {
        document.getElementById("errorMsg").innerHTML = errorMsg;
        document.getElementById("httpCode").innerHTML = httpCode;
    }
}

function main() {
    document.getElementById("year").innerHTML = getCurrentYear();
    hideFlashedMessages();
    displayHttpResponse();
    return 0;
} main();


/***** THESE FUNCTIONS ARE CALLED WITHIN HTML VIA BUTTONS *****/

function toggleNavbar() {
    // Elements we want to change are stored in the following array
    let activateElements = Array(
        document.getElementById("sideNav"),
        document.getElementById("navMenu"),
        document.getElementById("navItem"),
        document.getElementById("navBtn"),
        document.getElementById("menuBtn"),
    );
    // Iterate through the array and toggle the activated class.
    activateElements.forEach(element => element.classList.toggle("activated"))
}

function closeFlashedMsgs() {
    let msgBanner = document.getElementById("flashedMessage");
    msgBanner.style.display = 'none';
}