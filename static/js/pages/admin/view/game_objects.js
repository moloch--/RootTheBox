
function get_details(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);
    $.getJSON('/admin/ajax/objects?uuid=' + uuid + '&obj=' + obj, function(data) {
        $.each(data, function(key, value) {
            // console.log("#" + obj + "-" + key + " <- " + value);
            $("#" + obj + "-" + key).val(value);
        });
    });
}

/* Add click events */
$(document).ready(function() {

    /* Corporation */
    $("a[id^=edit-corporation-button]").click(function() {
        get_details("corporation", $(this).data("uuid"));
    });

    $("#edit-corporation-submit").click(function() {
        $("#edit-corporation-form").submit();
    });

    $("a[id^=delete-corporation-button]").click(function() {
        $("#delete-corporation-uuid").val($(this).data("uuid"));
    });

    $("#delete-corporation-submit").click(function() {
        $("#delete-corporation-form").submit();
    });

    /* Box */
    $("a[id^=edit-box-button]").click(function() {
        get_details("box", $(this).data("uuid"));
    });

    $("#edit-box-submit").click(function() {
        $("#edit-box-form").submit();
    });

    $("a[id^=delete-box-button]").click(function() {
        $("#delete-box-uuid").val($(this).data("uuid"));
    });

    $("#delete-box-submit").click(function() {
        $("#delete-box-form").submit();
    });

    /* Flag */
    $("a[id^=edit-flag-button]").click(function() {
        get_details("flag", $(this).data("uuid"));
    });

    $("#edit-flag-submit").click(function() {
        $("#edit-flag-form").submit();
    });

    $("a[id^=delete-flag-button]").click(function() {
        $("#delete-flag-uuid").val($(this).data("uuid"));
    });

    $("#delete-flag-submit").click(function() {
        $("#delete-flag-form").submit();
    });

    /* Hint */
    $("a[id^=edit-hint-button]").click(function() {
        get_details("hint", $(this).data("uuid"));
    });

    $("#edit-hint-submit").click(function() {
        $("#edit-hint-form").submit();
    });

    $("a[id^=delete-hint-button]").click(function() {
        $("#delete-hint-uuid").val($(this).data("uuid"));
    });

    $("#delete-hint-submit").click(function() {
        $("#delete-hint-form").submit();
    });

});