// Load "../static/dist/js/sb-admin-2.js" after all other files have loaded.
// Necessary to apply bootstrap skin's animations on all html code that is being loaded from other files (eg. sidebar).

function downloadJSAtOnload() {
    var element = document.createElement("script");
    element.src = "../static/dist/js/sb-admin-2.js";
    document.body.appendChild(element);
}
if (window.addEventListener)
    window.addEventListener("load", downloadJSAtOnload, false);
else if (window.attachEvent)
    window.attachEvent("onload", downloadJSAtOnload);
else window.onload = downloadJSAtOnload;


// Load html parts of the page
$( document ).ready(function() {

    // load header.html
    $( ".navbar-header" ).load( "/header" );

    // load sidebar.html
    // $( "#load_sidebar" ).load( "/sidebar");

    // load main content for the starting page
    $( "#page-wrapper" ).load( "/listofrules");

});