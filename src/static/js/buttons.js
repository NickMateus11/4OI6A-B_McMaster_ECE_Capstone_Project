
// Script to handle button POSTs

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
