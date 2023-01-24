function hideFlashedMessages() {
    var previousScrollPosition = window.scrollY;
    window.onscroll = function () {
        var currentScrollPosition = window.scrollY;
        if (previousScrollPosition > currentScrollPosition) {
            document.getElementById("flashedMessage").style.top = "0";
        }
        else {
            document.getElementById("flashedMessage").style.top = "-128px";
        }
        previousScrollPosition = currentScrollPosition;
    };
}
function getCurrentYear() {
    return new Date().getFullYear().toString();
}
function animateButtons() {
    var buttons = document.querySelectorAll('.r-btn');
    Array.prototype.forEach.call(buttons, function (b) {
        b.addEventListener('click', createRipple);
    });
    function createRipple(event) {
        var ripple = document.createElement('span');
        ripple.classList.add('ripple');
        var max = Math.max(this.offsetWidth, this.offsetHeight);
        ripple.style.width = ripple.style.height = max * 2 + 'px';
        var rect = this.getBoundingClientRect();
        ripple.style.left = event.clientX - rect.left - max + 'px';
        ripple.style.top = event.clientY - rect.top - max + 'px';
        this.appendChild(ripple);
    }
}
function main() {
    document.getElementById("year").innerHTML = getCurrentYear();
    hideFlashedMessages();
    animateButtons();
    return 0;
}
main();
/***** THESE FUNCTIONS ARE CALLED WITHIN HTML VIA BUTTONS *****/
function toggleNavbar() {
    // Elements we want to change are stored in the following array
    var activateElements = Array(document.getElementById("sideNav"), document.getElementById("navMenu"), document.getElementById("navItem"), document.getElementById("navBtn"), document.getElementById("menuBtn"));
    // Iterate through the array and toggle the activated class.
    activateElements.forEach(function (element) { return element.classList.toggle("activated"); });
}
function closeFlashedMsgs() {
    var msgBanner = document.getElementById("flashedMessage");
    msgBanner.style.display = 'none';
}
