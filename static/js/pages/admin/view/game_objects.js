
function get_details(obj, uuid) {
    $("#" + obj + "_uuid").val(uuid);
    $.getJSON('/admin/ajax/objects?uuid=' + uuid + '&obj=' + obj, function(data) {
        $.each(data, function(key, value) {
            // console.log("#" + obj + "_" + key + " -> " + value);
            $("#" + obj + "_" + key).val(value);
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




