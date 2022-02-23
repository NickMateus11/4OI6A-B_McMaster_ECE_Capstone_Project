
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