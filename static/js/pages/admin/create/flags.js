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

function buildChoice() {
    $("#token").val($('input[name=multichoice]:checked').next('input').val());
    var choicevals = $('input[name^=addmore');
    var choices = [];
    for (var i = 0; i < choicevals.length; i++) {
        if ($(choicevals[i]).val() !== "") {
            choices.push($(choicevals[i]).val());
        }
    }
    $("#choices").val(choices);
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

    $(".add-more").click(function(){ 
        var html = $(".copy").html();
        $(".after-add-more").siblings(":last").after(html);
    });

    $("body").on("click",".remove",function(){ 
        $(this).parents(".choice-control-group").remove();
    });

    $("form").submit(function(){
        if ($("#flagtype").val() === "choice") {
            buildChoice();
        }
    });
});