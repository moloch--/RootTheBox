$(document).ready(function() {

    /* Download Buttons */
    $("button[id^=file-upload-download]").click(function() {
        var uuid = $(this).data("uuid");
        window.open('/user/shares/download?uuid=' + uuid, '_newtab');
    });

    /* Delete Buttons */
    $("button[id^=delete-file-upload-button]").click(function() {
        $("#delete-file-upload-uuid").val($(this).data("uuid"));
    });

    $("#delete-file-upload-submit").click(function() {
        $("#delete-file-upload-form").submit();
    });

});