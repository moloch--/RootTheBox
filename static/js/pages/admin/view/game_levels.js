
function get_details(obj, uuid) {
    $("#" + obj + "_uuid").val(uuid);
    $.getJSON('/admin/ajax/objects?uuid=' + uuid + '&obj=' + obj, function(data) {
        $.each(data, function(key, value) {
            $("#" + obj + "-" + key).val(value);
        });
    });
}

/* Add click events */
$(document).ready(function() {

    /* Game Level */
    $("a[id^=edit-game-level-button]").click(function() {
        get_details("game_level", $(this).data("uuid"));
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