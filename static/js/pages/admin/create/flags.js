function getBoxFlags(box_uuid, flag_uuid) {
    data = {'uuid': box_uuid, 'obj': 'box', '_xsrf': getCookie("_xsrf")}
    $.post('/admin/ajax/objects', data, function(response) { 
        $('#edit-flag-lock').empty();
        $('#edit-flag-lock').append($('<option/>', { 
            value: "",
            text : ""
        }));
        $.each(response["flaglist"], function(uuid, name) {    
            if (uuid !== flag_uuid) {
                $('#edit-flag-lock').append($('<option/>', { 
                    value: uuid,
                    text : name
                }));
            } 
        });
    }, 'json');
}

function testToken() {
    submission = $("#test-token").val();
    token = $("#token").val();
    if (submission !== "" && token !== "") {
        flagtype = $("#flagtype").val();
        casesensitive = $("#case-sensitive").val();
        data = {'token': token, 'submission': submission, 'flagtype': flagtype, 'case': casesensitive, '_xsrf': getCookie("_xsrf")}
        $.post('/admin/tokentest/', data, function(response) { 
            if ("Success" in response) {
                if (response["Success"] === true) {
                    $("#testtrue").show();
                    $("#testfalse").hide();
                } else {
                    $("#testtrue").hide();
                    $("#testfalse").show();
                }
            } else {
                $("#testtrue").hide();
                $("#testfalse").hide();
            }
        }, 'json');
    } else {
        $("#testtrue").hide();
        $("#testfalse").hide();
    }
}

$(document).ready(function() {

    /* Popovers */
    $("#flag-name").popover({placement:'right', trigger:'hover'});
    $("#token").popover({placement:'right', trigger:'hover'});
    $("#description").popover({placement:'right', trigger:'hover'});
    $("#capture-message").popover({placement:'right', trigger:'hover'});
    $("#reward").popover({placement:'right', trigger:'hover'});
    $("#box-uuid").popover({placement:'right', trigger:'hover'});
    $("#case-button").popover({placement:'right', trigger:'hover'});

    $("#case-enable").click(function() {
        $("#case-sensitive").val(1);
        $("#case-enable-icon").removeClass("fa-square-o");
        $("#case-enable-icon").addClass("fa-check-square-o");
        $("#case-disable-icon").removeClass("fa-check-square-o");
        $("#case-disable-icon").addClass("fa-square-o");
        testToken();
    });
    $("#case-disable").click(function() {
        $("#case-sensitive").val(0);
        $("#case-disable-icon").removeClass("fa-square-o");
        $("#case-disable-icon").addClass("fa-check-square-o");
        $("#case-enable-icon").removeClass("fa-check-square-o");
        $("#case-enable-icon").addClass("fa-square-o");
        testToken();
    });
    $("#box-uuid").change(function() {
        getBoxFlags($("#box-uuid  option:selected").val(), '');
    });
    $("#test-token").change(function() {
        testToken();
    });
    $("#token").change(function() {
        testToken();
    });
});