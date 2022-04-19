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