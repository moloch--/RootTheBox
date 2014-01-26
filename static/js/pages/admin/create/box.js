$(document).ready(function() {

    $("button[id^=os-button]").click(function() {
        $("#operating-system").val($(this).data("os"));
    });

});