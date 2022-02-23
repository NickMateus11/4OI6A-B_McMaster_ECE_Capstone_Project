
// Script to handle button POSTs

$(function() {
    $('#START').bind('click', function() {
        $.getJSON('/print_hello',
            function(data) {
        //do nothing
        });
        return false;
    });
});