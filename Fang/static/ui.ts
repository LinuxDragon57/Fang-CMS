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


function main() {
    document.getElementById("year").innerHTML = getCurrentYear();
    hideFlashedMessages();

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