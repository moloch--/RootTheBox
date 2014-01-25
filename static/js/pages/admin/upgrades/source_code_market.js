
function add_src(box_uuid) {
    $("#add_box_uuid").val(box_uuid);
}

function del_src(box_uuid) {
    $("#del_box_uuid").val(box_uuid);
}


$(document).ready(function() {

    $("#add-source-button").click(function() {
        $("#add_box_uuid").val($(this).data("uuid"));
    });

    $("#add-source-submit").click(function() {
        $("#add-source-form").submit();
    });

    $("#delete-source-button").click(function() {
        $("#delete_box_uuid").val($(this).data("uuid"));
    });

    $("#delete-source-submit").click(function() {
        $("#delete-source-form").submit();
    });

});