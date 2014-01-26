$(document).ready(function() {

    /* Accept */
    $("a[id^=accept-bribe-button]").click(function() {
        $("#accept-bribe-uuid").val($(this).data("uuid"));
    });

    $("#accept-bribe-submit").click(function() {
        $("#accept-bribe-form").submit();
    });

    /* Decline */
    $("a[id^=decline-bribe-button]").click(function() {
        $("#decline-bribe-uuid").val($(this).data("uuid"));
    });

    $("#decline-bribe-submit").click(function() {
        $("#decline-bribe-form").submit();
    });

    /* Complete */
    $("a[id^=complete-bribe-button]").click(function() {
        $("#complete-bribe-uuid").val($(this).data("uuid"));
    });

    $("#complete-bribe-submit").click(function() {
        $("#complete-bribe-form").submit();
    });

});