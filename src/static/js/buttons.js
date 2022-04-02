
// Script to handle button presses WITHOUT redirection
jQuery(document).ready(function($) {
    $('#START').bind('click', function() {
        $.getJSON('/start',
            function(data) {
        //do nothing
        });
        return false;
    });

    $('#STOP').bind('click', function() {
        $.getJSON('/stop',
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

    $('#RESET').bind('click', function() {
        $.getJSON('/reset',
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

    $('#CENTER').bind('click', function() {
        $.getJSON('/center',
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

    // use standard HTML form submission instead
    // $('#PAYLOAD').bind('click', function() {
    //     $.post('/',
    //         function(data) {
        //do nothing
    //     });
    //     return false;
    // });
    //// *** Must allow redirect for file to download - so we don't need this here
    // $('#CAPTURE').bind('click', function() {
    //     $.getJSON('/capture',
    //         function(data) {
    //     //do nothing
    //     });
    //     return false;
    // });


    $(".clickable-cell").click(function() {
        $.post(
            '/grid_click',
            JSON.stringify({"cell": $(this).attr('id')}),
            function(data) {
                //do nothing
            });
        // console.log($(this).attr('id'))
        return false;
    });
});
