$(document).ready(function() {

    $("#create-paste").click(function() {
        $.get('/user/share/pastebin/create', function(data) {
            $('#display-paste').html(data);
        });
    });

    $("a[id^=view-paste]").click(function() {
        var uuid = $(this).data("uuid");
        $.get('/user/share/pastebin/display?paste_uuid=' + uuid, function(data) {
            $('#display-paste').html(data);
            $("#create-paste").click(function() {
                $.get('/user/share/pastebin/create', function(data) {
                    $('#display-paste').html(data);
                });
            });
            $("#delete-paste").click(function() {
                var uuid = $(this).data("uuid");
                $('#delete-paste-uuid').val(uuid);
                $("#delete-paste-form").submit();
            });
        });
    });

});