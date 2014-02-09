function get_details(obj, uuid) {
    $.getJSON('/admin/ajax/objects?uuid=' + uuid + '&obj=' + obj, function(data) {
        $.each(data, function(key, value) {
            $("#" + obj + "-" + key).val(value);
        });
    });
}

$(document).ready(function() {

    /* Team */
    $("a[id^=edit-team-button]").click(function() {
        get_details("team", $(this).data("uuid"));
    });

    $("#edit-team-submit").click(function() {
        $("#edit-team-form").submit();
    });

    /* User */
    $("a[id^=edit-user-button]").click(function() {
        get_details("user", $(this).data("uuid"));
    });

    $("#edit-user-submit").click(function() {
        $("#edit-user-form").submit();
    });

    $("a[id^=delete-user-button]").click(function() {
        $("#delete-user-uuid").val($(this).data("uuid"));
    });

    $("#delete-user-submit").click(function() {
        $("#delete-user-form").submit();
    });

    $("a[id^=lock-user-button]").click(function() {
        $("#lock-user-uuid").val($(this).data("uuid"));
        $("#lock-user-form").submit();
    });

    /* Other */
    $("a[id^=reveal-hash-button]").click(function() {
        alert($(this).data("bank-hash"));
    });

});
