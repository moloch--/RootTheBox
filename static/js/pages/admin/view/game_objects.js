
function get_details(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);
    $.getJSON('/admin/ajax/objects?uuid=' + uuid + '&obj=' + obj, function(data) {
        $.each(data, function(key, value) {
            // console.log("#" + obj + "-" + key + " <- " + value);
            $("#" + obj + "-" + key).val(value);
        });
    });
}


function set_box_uuid(ipv, box_uuid) {
    $("#" + ipv + "_uuid").val(box_uuid);
}
function set_delip(ip) {
    $("#delip").val(ip);
}
function set_delflag(flag_uuid) {
    $("#delflag").val(flag_uuid);
}
function set_delhint(uuid) {
    $("#delhint").val(uuid);
}


/* Add click events */
$(document).ready(function() {

    /* Corporation */
    $("#edit-corporation-button").click(function() {
        get_details("corporation", $(this).data("uuid"));
    });

    $("#edit-corporation-submit").click(function() {
        $("#edit-corporation-form").submit();
    });

    $("#delete-corporation-button").click(function() {
         $("#delete-corporation-uuid").val($(this).data("uuid"));
    });

    $("#delete-corporation-submit").click(function() {
         $("#delete-corporation-form").submit();
    });

    /* Box */
    $("#edit-box-button").click(function() {
        get_details("box", $(this).data("uuid"));
    });

    $("#edit-box-submit").click(function() {
        $("#edit-box-form").submit();
    });

    $("#delete-box-button").click(function() {
         $("#delete-box-uuid").val($(this).data("uuid"));
    });

    $("#delete-box-submit").click(function() {
         $("#delete-box-form").submit();
    });

    /* Flag */
    $("#edit-flag-button").click(function() {
        get_details("flag", $(this).data("uuid"));
    });

    $("#edit-flag-submit").click(function() {
        $("#edit-flag-form").submit();
    });

    $("#delete-flag-button").click(function() {
         $("#delete-flag-uuid").val($(this).data("uuid"));
    });

    $("#delete-flag-submit").click(function() {
         $("#delete-flag-form").submit();
    });

    /* Hint */
    $("#edit-hint-button").click(function() {
        get_details("hint", $(this).data("uuid"));
    });

    $("#edit-hint-submit").click(function() {
        $("#edit-hint-form").submit();
    });

    $("#delete-hint-button").click(function() {
         $("#delete-hint-uuid").val($(this).data("uuid"));
    });

    $("#delete-hint-submit").click(function() {
         $("#delete-hint-form").submit();
    });

});