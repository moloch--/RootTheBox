
function get_details(obj, uuid) {
    $("#" + obj + "_uuid").val(uuid);
    $.getJSON('/admin/ajax/objects?uuid=' + uuid + '&obj=' + obj, function(data) {
        $.each(data, function(key, value) {
            $("#" + obj + "_" + key).val(value);
        });
    });
}

function toggle_lock(uuid) {
    $("#lock_uuid").value = uuid;
    $("#lock_form").submit();
}

$(document).ready(function() {

    $("#edit-team-submit").click(function() {
        $("#edit-team-form").submit();
    });

    $("#edit-user-submit").click(function() {
        $("#edit-user-form").submit();
    });

    $("#edit-user-button").click(function() {
        var uuid = $(this).data("user-uuid");
        var obj = $(this).data("object");
        $.getJSON('/admin/ajax/objects?uuid=' + uuid + '&obj=' + obj, function(data) {
            $.each(data, function(key, value) {
                $("#" + obj + "_" + key).val(value);
            });
        });
    });

});
