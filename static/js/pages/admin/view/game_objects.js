function getDetails(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);
    data = {'uuid': uuid, 'obj': obj, '_xsrf': getCookie("_xsrf")}
    $.post('/admin/ajax/objects', data, function(response) {
        $.each(response, function(key, value) {
            if (obj === "hint") {
                if (key === "flaglist") {
                    $('#hint-flag_uuid').empty();
                    $('#hint-flag_uuid').append($('<option/>', { 
                        value: "",
                        text : ""
                    }));
                    $.each(value, function (uuid, name) {
                        $('#hint-flag_uuid').append($('<option/>', { 
                            value: uuid,
                            text : name
                        }));
                    });
                    $('#hint-flag_uuid option[value=' + response["flag_uuid"] + ']').prop('selected',true);   
                } else if (key !== "flag_uuid") {
                    $("#" + obj + "-" + key).val(value);
                }
            } else if (obj === "box" && key === "category") {
                if (value.length > 0) {
                    $('#edit-box-category option[value=' + value + ']').prop('selected',true);
                } else {
                    $('#edit-box-category option[value=""]').prop('selected',true);
                }
            } else if (obj === "box" && key === "corporation") {
                $('#edit-box-corporation option[value=' + value + ']').prop('selected',true);
            } else if (obj === "flag" && key === "lock_uuid") {
                if (value.length > 0) {
                    $('#edit-flag-lock option[value=' + value + ']').prop('selected',true);
                } else {
                    $('#edit-flag-lock option[value=""]').prop('selected',true);
                }
            } else {
                $("#" + obj + "-" + key).val(value);    
            }
        });
        if (response["case-sensitive"] === 0) {
            $("#case-disable-icon").removeClass("fa-square-o");
            $("#case-disable-icon").addClass("fa-check-square-o");
            $("#case-enable-icon").removeClass("fa-check-square-o");
            $("#case-enable-icon").addClass("fa-square-o");
        }
    }, 'json');
}

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
    token = $("#flag-token").val();
    if (submission !== "" && token !== "") {
        flagtype = $("#flag-flagtype").val();
        casesensitive = $("#flag-case-sensitive").val();
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

/* Add click events */
$(document).ready(function() {

    /* Corporation */
    $("a[id^=edit-corporation-button]").click(function() {
        getDetails("corporation", $(this).data("uuid"));
    });

    $("#edit-corporation-submit").click(function() {
        $("#edit-corporation-form").submit();
    });

    $("a[id^=delete-corporation-button]").click(function() {
        $("#delete-corporation-uuid").val($(this).data("uuid"));
    });

    $("#delete-corporation-submit").click(function() {
        $("#delete-corporation-form").submit();
    });

    /* Box */
    $("a[id^=edit-box-button]").click(function() {
        getDetails("box", $(this).data("uuid"));
        $("#edit-box-corporation").val($(this).data("corporation-uuid"));
    });

    $("#edit-box-submit").click(function() {
        $("#edit-box-form").submit();
    });

    $("a[id^=delete-box-button]").click(function() {
        $("#delete-box-uuid").val($(this).data("uuid"));
    });

    $("#delete-box-submit").click(function() {
        $("#delete-box-form").submit();
    });

    /* IP Address */
    $("#add-ip-address-submit").click(function() {
        $("#add-ip-address-form").submit();
    });

    $("a[id^=add-ip-address-button]").click(function() {
        $("#add-ip-address-uuid").val($(this).data("uuid"));
    });

    $("#delete-ip-address-submit").click(function() {
        $("#delete-ip-address-form").submit();
    });

    $("a[id^=delete-ip-address-button]").click(function() {
        $("#delete-ip-address-uuid").val($(this).data("uuid"));
    });

    /* Flag */
    $("a[id^=edit-flag-button]").click(function() {
        getBoxFlags($(this).data("box-uuid"), $(this).data("uuid"));
        getDetails("flag", $(this).data("uuid"));
        $("#test-token").val("");
        $("#testtrue").hide();
        $("#testfalse").hide();
        $("#edit-flag-box").val($(this).data("box-uuid"));
        if ($(this).data("flagtype") === "static" || $(this).data("flagtype") === "regex") {
            $("#casegroup").show();
        } else {
            $("#casegroup").hide();
        }
    });

    $("#edit-flag-submit").click(function() {
        $("#edit-flag-form").submit();
    });

    $("a[id^=delete-flag-button]").click(function() {
        $("#delete-flag-uuid").val($(this).data("uuid"));
    });

    $("#delete-flag-submit").click(function() {
        $("#delete-flag-form").submit();
    });

    $("#case-enable").click(function() {
        $("#flag-case-sensitive").val(1);
        $("#case-enable-icon").removeClass("fa-square-o");
        $("#case-enable-icon").addClass("fa-check-square-o");
        $("#case-disable-icon").removeClass("fa-check-square-o");
        $("#case-disable-icon").addClass("fa-square-o");
        testToken();
    });
    $("#case-disable").click(function() {
        $("#flag-case-sensitive").val(0);
        $("#case-disable-icon").removeClass("fa-square-o");
        $("#case-disable-icon").addClass("fa-check-square-o");
        $("#case-enable-icon").removeClass("fa-check-square-o");
        $("#case-enable-icon").addClass("fa-square-o");
        testToken();
    });

    /* Hint */
    $("a[id^=edit-hint-button]").click(function() {
        getDetails("hint", $(this).data("uuid"));
    });

    $("#edit-hint-submit").click(function() {
        $("#edit-hint-form").submit();
    });

    $("a[id^=delete-hint-button]").click(function() {
        $("#delete-hint-uuid").val($(this).data("uuid"));
    });

    $("#delete-hint-submit").click(function() {
        $("#delete-hint-form").submit();
    });

    /* Avatar */
    $(".boxavatarimg").click(function() {
        var filename = $(this).attr('value');
        $("#box_avatar_select").val(filename);
        $("#avatarfilename").text("File: " + filename.replace("box/",""));
        $("#avatarclose").click();
    });
    $("#box-avatar").change(function(){
        $("#avatarfilename").text("File: " + $(this).val());
        $("#box_avatar_select").val("");
    });

    $("#uploadbutton").click(function(){
        $("#box-avatar").click(); 
    });
    $("#test-token").change(function() {
        testToken();
    });
    $("#flag-token").change(function() {
        testToken();
    });
});