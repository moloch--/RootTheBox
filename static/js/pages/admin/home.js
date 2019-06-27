$(document).ready(function() {

    updateGitStatus();

    $("#start-game-button").click(function() {
        $("#start-game").val("true");
        $("#start-game-form").submit();
    });

    $("#stop-game-button").click(function() {
        $("#start-game").val("false");
        $("#start-game-form").submit();
    });

    $("#suspend-registration-button").click(function() {
        $("#start-game").val("true");
        $("#suspend-registration").val("true");
        $("#start-game-form").submit();
    });

    $("#resume-registration-button").click(function() {
        $("#start-game").val("true");
        $("#suspend-registration").val("false");
        $("#start-game-form").submit();
    });

    $("#resume-scoreboard-button").click(function() {
        $("#start-game").val("true");
        $("#freeze-scoreboard").val("false");
        $("#start-game-form").submit();
    });

    if ($("#automatic-ban").val() === "true") {
        $("#automatic-ban-enable-icon").removeClass("fa-square-o");
        $("#automatic-ban-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#automatic-ban-disable-icon").removeClass("fa-square-o");
        $("#automatic-ban-disable-icon").addClass("fa-check-square-o");
        $("#threshold-size").prop('disabled', true);
    }

    $("#ban-ip-button").click(function() {
        $("#ban-ip").val($(this).data("ip"));
        $("#ban-ip-form").submit();
    });

    $("#clear-ip-button").click(function() {
        $("#clear-ip").val($(this).data("ip"));
        $("#clear-ip-form").submit();
    });

    $("#timer-submit").click(function() {
        $("#timer-form").submit();
    });

    $("#message-submit").click(function() {
        $("#message-form").submit();
    });

    $("#updatebutton").click(function() {
        $("#update-rtb").hide();
        $("#gitstatus").html('<hr /><i class="fa fa-info-circle gitstatus info"></i>&nbsp;&nbsp;Updating Root the Box...');
        var xsrf = $("#update-rtb").prop("_xsrf");
        $.ajax({
            type: "POST",
            url: "/admin/gitstatus",
            data: {"_xsrf": $(xsrf).val()},
            success: function() {
                setTimeout(function(){
                    updateGitStatus();
                }, 1500);
            }
          });
          return false;
    });

    /* Enable/disable buttons */
    $("#automatic-ban-enable").click(function() {
        $("#automatic-ban").val("true");
        $("#automatic-ban-enable-icon").removeClass("fa-square-o");
        $("#automatic-ban-enable-icon").addClass("fa-check-square-o");
        $("#automatic-ban-disable-icon").removeClass("fa-check-square-o");
        $("#automatic-ban-disable-icon").addClass("fa-square-o");
        $("#threshold-size").prop('disabled', false);
    });

    $("#automatic-ban-disable").click(function() {
        $("#automatic-ban").val("false");
        $("#automatic-ban-disable-icon").removeClass("fa-square-o");
        $("#automatic-ban-disable-icon").addClass("fa-check-square-o");
        $("#automatic-ban-enable-icon").removeClass("fa-check-square-o");
        $("#automatic-ban-enable-icon").addClass("fa-square-o");
        $("#threshold-size").prop('disabled', true);
    });

});

function updateGitStatus() {
    $.get("/admin/gitstatus", function(status) {
        if (status.includes("Your branch is behind")) {
            status = '<hr /><i class="fa fa-info-circle gitstatus info"></i>&nbsp;&nbsp;' +
                '<span title="commands: git fetch ; git status">' + status + '</span>';
            $("#update-rtb").show();
        } else if (status.includes("Your branch is up to date")) {
            status = '<hr /><i class="fa fa-check-circle gitstatus ok"></i>&nbsp;&nbsp;Root the Box is up to date.';
        } else {
            if (status.indexOf(":") > 0) {
                status = status.slice(0,status.indexOf(":")) + "."
            }
            status = '<hr /><i class="fa fa-exclamation-circle gitstatus warn"></i>&nbsp;&nbsp;' +
                '<span title="commands: git fetch ; git status">git: ' + status + '</span>';
        }
        $("#gitstatus").html(status);
    });
}