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

/* Add click events */
$(document).ready(function() {

    /* Game Level */
    $("a[id^=edit-game-level-button]").click(function() {
        getDetails("game_level", $(this).data("uuid"));
    });

    $("#edit-game-level-submit").click(function() {
        $("#edit-game-level-form").submit();
    });

    $("a[id^=delete-game-level-button]").click(function() {
         $("#delete-game-level-uuid").val($(this).data("uuid"));
    });

    $("#delete-game-level-submit").click(function() {
         $("#delete-game-level-form").submit();
    });

    /* Switch Level */
    $("a[id^=switch-level-button]").click(function() {
        $("#game-level-uuid").val($(this).data("level-uuid"));
        $("#box-uuid").val($(this).data("box-uuid"));
    });

    $("#switch-level-submit").click(function() {
        $("#switch-level-form").submit();
    });

});