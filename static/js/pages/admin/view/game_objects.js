function getDetails(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);
    data = {'uuid': uuid, 'obj': obj, '_xsrf': getCookie("_xsrf")};
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
                    if (response["flag_uuid"] !== "") {
                        $('#hint-flag_uuid option[value=' + response["flag_uuid"] + ']').prop('selected',true);  
                    }
                } else if (key !== "flag_uuid") {
                    $("#" + obj + "-" + key).val(value);
                }
            } else if (obj === "box" && key === "category") {
                if (value.length > 0) {
                    $('#edit-box-category option[value=' + value + ']').prop('selected',true);
                } else {
                    $('#edit-box-category option[value=""]').prop('selected',true);
                }
            } else if (obj === "box" && key === "operating_system") {
                if (value === "?") {
                    $("#type_unknown").prop('selected',true);
                } else if (value.length > 0) {
                    $('#edit-box-operating_system option[value=' + value + ']').prop('selected',true);
                }
            } else if (obj === "box" && key === "corporation") {
                $('#edit-box-corporation option[value=' + value + ']').prop('selected',true);
            } else if (obj === "box" && key === "game_level") {
                $('#edit-box-game-level option[value=' + value + ']').prop('selected',true);
            } else if (obj === "box" && key === "flag_submission_type") {
                if (value === "CLASSIC") {
                    $('#box-flag-submission-type-classic').click();
                } else if(value === "SINGLE_SUBMISSION_BOX") {
                    $('#box-flag-submission-type-single-box').click();
                }
            } else if (obj === "flag" && key === "lock_uuid") {
                if (value.length > 0) {
                    $('#edit-flag-lock option[value=' + value + ']').prop('selected',true);
                } else {
                    $('#edit-flag-lock option[value=""]').prop('selected',true);
                }
            } else if (obj === "flag" && key === "choices") {
                var token = response["token"];
                var choices = $.parseJSON(value);
                var appendarea = $(".after-add-more");
                appendarea.nextAll().remove();
                if (choices.length > 0) {
                    for (var i=0; i < choices.length; i++){
                        var html = $(".copy").html();
                        if (i === 0) {
                            var item = appendarea;
                        } else if (i === 1) { 
                            var newadd = appendarea.after(html);
                            var item = $(newadd.next());
                        } else {
                            var newadd = appendarea.siblings(":last").after(html);
                            var item = $(newadd.next());
                        }
                        var textbox = item.find("input[name^=choice]");
                        $(textbox).val(choices[i].choice);
                        $(textbox).prop("name", "choice-uuid-" + choices[i].uuid + "");
                        $(textbox).prop("uuid", choices[i].uuid);
                        if (token === choices[i].choice) {
                            var radio = item.find("input[name=multichoice]");
                            radio.prop("checked", true);
                        }
                    }
                    $('input[name=multichoice]').click(function(){
                        $("#flag-token").val($(this).next('input').val());
                    });
                    $('input[name^=choice]').change(function(){
                        $("#flag-token").val($('input[name=multichoice]:checked').next('input').val());
                    });
                }  
            } else if (obj === "flag" && key === "name") {
                // Leave name value blank if it's auto-generated based on order
                if (value !== "Question " + response.order) {
                    $("#" + obj + "-" + key).val(value);
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

function setFlagType(flagtype) {
    var staticval = ["static", "regex", "datetime"]
    $(".typeoption").hide();
    if (staticval.includes(flagtype)) {
        for (i in staticval) {
            $("#edit-type-" + staticval[i]).show();
        }
    } else {
        $("edit-type-" + flagtype).show();
    }
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
        flagtype = $("#edit-flag-type").val();
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

function adjustNavigation() {
    if ($("footer").position().top > $("#navWrapper").outerHeight(true)) {
        let topOffset = 60;
        $("#navWrapper").css({top: topOffset, bottom: "auto"});
    } else {
        let bottomOffset = 20;
        let wrapperpos = $("#navWrapper").outerHeight(true) + bottomOffset;
        let footerpos = $("footer").position().top + $(document).scrollTop()
        if (footerpos < wrapperpos){
            let floatingOffset = footerpos - wrapperpos + 10
            $("#navWrapper").css({top: "auto", bottom: floatingOffset});        
        } else {
            $("#navWrapper").css({top: "auto", bottom: bottomOffset});     
        }
    }        
}

/* Add click events */
$(document).ready(function() {
    var reader = new commonmark.Parser({smart: true});
    var writer = new commonmark.HtmlRenderer({safe: true, softbreak: "<br />"});

    /* Markdown */
    $(".markdown").each(function() {
        var parsed = reader.parse($(this).text());
        $(this).html(writer.render(parsed).trim());
    });

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

    $("a[id^=lock-box-button]").click(function() {
        $("#lock-box-uuid").val($(this).data("uuid"));
        $("#lock-box-form").submit();
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

    $("#box-flag-submission-type-classic").click(function() {
        $("#box-flag_submission_type").val("CLASSIC");
        $("#box-flag-submission-type-classic-icon").removeClass("fa-square-o");
        $("#box-flag-submission-type-classic-icon").addClass("fa-check-square-o");
        $("#box-flag-submission-type-single-boxe-icon").removeClass("fa-check-square-o");
        $("#box-flag-submission-type-single-box-icon").addClass("fa-square-o");
    });
    $("#box-flag-submission-type-single-box").click(function() {
        $("#box-flag_submission_type").val("SINGLE_SUBMISSION_BOX");
        $("#box-flag-submission-type-classic-icon").removeClass("fa-check-square-o");
        $("#box-flag-submission-type-classic-icon").addClass("fa-square-o");
        $("#box-flag-submission-type-single-box-icon").removeClass("fa-square-o");
        $("#box-flag-submission-type-single-box-icon").addClass("fa-check-square-o");
    });

    /* Flag */
    $("a[id^=edit-flag-button]").click(function() {
        getBoxFlags($(this).data("box-uuid"), $(this).data("uuid"));
        getDetails("flag", $(this).data("uuid"));
        setFlagType($(this).data("flagtype"));
        $("#test-token").val("");
        $("#testtrue").hide();
        $("#testfalse").hide();
        $("#edit-flag-box").val($(this).data("box-uuid"));
        $("#edit-flag-type").val($(this).data("flagtype"));
        if ($(this).data("flagtype") === "static" || $(this).data("flagtype") === "regex") {
            $("#casegroup").show();
        } else {
            $("#casegroup").hide();
        }
        if ($(this).data("flagtype") === "choice") {
            $("#testflaggroup").hide();
            $("#flagtokengroup").hide();
            $("#choicegroup").show();
        } else {
            $("#testflaggroup").show();
            $("#flattokengroup").show();
            $("#choicegroup").hide();
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
    $(".add-more").click(function(){
        var html = $(".copy").html();
        var siblings = $(".after-add-more").siblings(":last");
        if (siblings.length > 0) {
            siblings.after(html);
        } else {
            $(".after-add-more").after(html);
        }
    });

    $("body").on("click",".remove",function(){ 
        $(this).parents(".choice-control-group").remove();
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
        $("#avatarfilename").text("File: " + filename.replace("box/","").replace(/^C:\\fakepath\\/, ""));
        $("#avatarclose").click();
    });
    $("#box-avatar").change(function(){
        $("#avatarfilename").text("File: " + $(this).val().replace(/^C:\\fakepath\\/, ""));
        $("#box_avatar_select").val("");
    });
    $("#removeavatar").click(function(){
        $("#avatarfilename").text("File: None");
        $("#box_avatar_select").val("none");
    });
    $("#change_avatar_button").click(function(){
        $("#edit-box-modal").hide(); 
    });
    $("#avatarclose").click(function(){
        $("#edit-box-modal").show(); 
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
    $(function () {
        $('#hint-description').markdownToolbar(false, reader, writer);
        $('#box-description').markdownToolbar(false, reader, writer);
        $('#flag-description').markdownToolbar(false, reader, writer);
    })
    /* reorder flags */
    var fixHelperModified = function(e, tr) {
        var $originals = tr.children();
        var $helper = tr.clone();
        $helper.children().each(function(index) {
            $(this).width($originals.eq(index).width())
        });
        return $helper;
    },
        updateIndex = function(e, ui) {
            hintcheck = {}
            hints = ui.item.closest(".startflags").siblings(".starthints");
            $('td.index', ui.item.parent()).each(function (i) {
                var inc = i+1;
                $(this).text(inc);
                var flagname = $(this).next().next();
                var beforename = flagname.text();
                if (beforename.startsWith("Question ")) {
                    var aftername = "Question " + inc;
                    if (beforename !== aftername) {
                        flagname.text("Question " + inc);
                        hintcheck[beforename] = aftername;
                    }
                }
                data = {'uuid': $(this).data("uuid"), 'order': (inc), '_xsrf': getCookie("_xsrf")};
                $.post('/admin/edit/flag_order', data);
            });
            hintupdate = hints.find(".flagname");
            for (var i = 0; i < hintupdate.length; i++) {
                fname = $(hintupdate[i]).text();
                if (fname in hintcheck) {
                    $(hintupdate[i]).text(hintcheck[fname]);
                }
            }
        };
    
    $(".sort tbody").sortable({
        helper: fixHelperModified,
        stop: updateIndex
    }).disableSelection();

    $(document).on('scroll', function(){
        adjustNavigation();
    })

    $(window).on('resize', function() {
        adjustNavigation();
    });

});