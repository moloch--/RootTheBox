function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function getDetails(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);
    data = {'uuid': uuid, 'obj': obj, '_xsrf': getCookie("_xsrf")}
    $.post('/admin/ajax/objects', data, function(response) {
        $.each(response, function(key, value) {
            $("#" + obj + "-" + key).val(value);
        });
    }, 'json');
}

$(document).ready(function() {

    /* Team */
    $("a[id^=edit-team-button]").click(function() {
        getDetails("team", $(this).data("uuid"));
    });

    $("#edit-team-submit").click(function() {
        $("#edit-team-form").submit();
    });

    /* User */
    $("a[id^=edit-user-button]").click(function() {
        getDetails("user", $(this).data("uuid"));
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
