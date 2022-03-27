
// Script to handle button presses WITHOUT redirection

$('#START').bind('click', function() {
    $.getJSON('/print_hello',
        function(data) {
    //do nothing
    });
    return false;
});

$('#STOP').bind('click', function() {
    $.getJSON('/print_test',
        function(data) {
    //do nothing
    });
    return false;
});

$('#CALIBRATE').bind('click', function() {
    $.getJSON('/calibrate',
        function(data) {
    //do nothing
    });
    return false;
});

$('#UP').bind('click', function() {
    $.getJSON('/up',
        function(data) {
    //do nothing
    });
    return false;
});

$('#DOWN').bind('click', function() {
    $.getJSON('/down',
        function(data) {
    //do nothing
    });
    return false;
});


$('#LEFT').bind('click', function() {
    $.getJSON('/left',
        function(data) {
    //do nothing
    });
    return false;
});

$('#RIGHT').bind('click', function() {
    $.getJSON('/right',
        function(data) {
    //do nothing
    });
    return false;
});

$('#PAYLOAD').bind('click', function() {
    $.postJSON('/',
        function(data) {
    //do nothing
    });
    return false;
});
//// *** Must allow redirect for file to download - so we don't need this here
// $('#CAPTURE').bind('click', function() {
//     $.getJSON('/capture',
//         function(data) {
//     //do nothing
//     });
//     return false;
// });
