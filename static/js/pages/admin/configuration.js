$(document).ready(function() {

    /* Disable feilds if their corisponding features are disabled */
    if ($("#use-bots").val() === "false") {
        $('#bot-reward').prop('disabled', true);
    }
    if ($("#use-black-market").val() === "false") {
        $('#password-upgrade-cost').prop('disabled', true);
        $('#bribe-cost').prop('disabled', true);
    }

    /* Set initial state for buttons */
    if ($("#restrict-registration").val() === "true") {
        $("#restrict-registration-enable-icon").removeClass("fa-square-o");
        $("#restrict-registration-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#restrict-registration-disable-icon").removeClass("fa-square-o");
        $("#restrict-registration-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#public-teams").val() === "true") {
        $("#public-teams-enable-icon").removeClass("fa-square-o");
        $("#public-teams-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#public-teams-disable-icon").removeClass("fa-square-o");
        $("#public-teams-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#use-bots").val() === "true") {
        $("#use-bots-enable-icon").removeClass("fa-square-o");
        $("#use-bots-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#use-bots-disable-icon").removeClass("fa-square-o");
        $("#use-bots-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#use-black-market").val() === "true") {
        $("#use-black-market-enable-icon").removeClass("fa-square-o");
        $("#use-black-market-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#use-black-market-disable-icon").removeClass("fa-square-o");
        $("#use-black-market-disable-icon").addClass("fa-check-square-o");
    }

    /* Button callbacks */
    $("#restrict-registration-enable").click(function() {
        $("#restrict-registration").val("true");
        $("#restrict-registration-enable-icon").removeClass("fa-square-o");
        $("#restrict-registration-enable-icon").addClass("fa-check-square-o");
        $("#restrict-registration-disable-icon").removeClass("fa-check-square-o");
        $("#restrict-registration-disable-icon").addClass("fa-square-o");
    });
    $("#restrict-registration-disable").click(function() {
        $("#restrict-registration").val("false");
        $("#restrict-registration-disable-icon").removeClass("fa-square-o");
        $("#restrict-registration-disable-icon").addClass("fa-check-square-o");
        $("#restrict-registration-enable-icon").removeClass("fa-check-square-o");
        $("#restrict-registration-enable-icon").addClass("fa-square-o");
    });

    $("#public-teams-enable").click(function() {
        $("#public-teams").val("true");
        $("#public-teams-enable-icon").removeClass("fa-square-o");
        $("#public-teams-enable-icon").addClass("fa-check-square-o");
        $("#public-teams-disable-icon").removeClass("fa-check-square-o");
        $("#public-teams-disable-icon").addClass("fa-square-o");
    });
    $("#public-teams-disable").click(function() {
        $("#public-teams").val("false");
        $("#public-teams-disable-icon").removeClass("fa-square-o");
        $("#public-teams-disable-icon").addClass("fa-check-square-o");
        $("#public-teams-enable-icon").removeClass("fa-check-square-o");
        $("#public-teams-enable-icon").addClass("fa-square-o");
    });

    $("#use-bots-enable").click(function() {
        $("#use-bots").val("true");
        $("#use-bots-enable-icon").removeClass("fa-square-o");
        $("#use-bots-enable-icon").addClass("fa-check-square-o");
        $("#use-bots-disable-icon").removeClass("fa-check-square-o");
        $("#use-bots-disable-icon").addClass("fa-square-o");
        $('#bot-reward').prop('disabled', false);
    });
    $("#use-bots-disable").click(function() {
        $("#use-bots").val("false");
        $("#use-bots-disable-icon").removeClass("fa-square-o");
        $("#use-bots-disable-icon").addClass("fa-check-square-o");
        $("#use-bots-enable-icon").removeClass("fa-check-square-o");
        $("#use-bots-enable-icon").addClass("fa-square-o");
        $('#bot-reward').prop('disabled', true);
    });

    $("#use-black-market-enable").click(function() {
        $("#use-black-market").val("true");
        $("#use-black-market-enable-icon").removeClass("fa-square-o");
        $("#use-black-market-enable-icon").addClass("fa-check-square-o");
        $("#use-black-market-disable-icon").removeClass("fa-check-square-o");
        $("#use-black-market-disable-icon").addClass("fa-square-o");
        $('#password-upgrade-cost').prop('disabled', false);
        $('#bribe-cost').prop('disabled', false);
    });
    $("#use-black-market-disable").click(function() {
        $("#use-black-market").val("false");
        $("#use-black-market-disable-icon").removeClass("fa-square-o");
        $("#use-black-market-disable-icon").addClass("fa-check-square-o");
        $("#use-black-market-enable-icon").removeClass("fa-check-square-o");
        $("#use-black-market-enable-icon").addClass("fa-square-o");
        $('#password-upgrade-cost').prop('disabled', true);
        $('#bribe-cost').prop('disabled', true);
    });

    /* Enable popovers */
    $("#game-name").popover({placement:'right', trigger:'hover'});
    $("#restrict-registration-button").popover({placement:'right', trigger:'hover'});
    $("#public-teams-button").popover({placement:'right', trigger:'hover'});
    $("#max-team-size").popover({placement:'right', trigger:'hover'});
    $("#min-user-password-length").popover({placement:'right', trigger:'hover'});
    $("#max-password-length").popover({placement:'right', trigger:'hover'});
    $("#use-bots-button").popover({placement:'right', trigger:'hover'});
    $("#bot-reward").popover({placement:'right', trigger:'hover'});
    $("#use-black-market-button").popover({placement:'right', trigger:'hover'});
    $("#password-upgrade-cost").popover({placement:'right', trigger:'hover'});
    $("#bribe-cost").popover({placement:'right', trigger:'hover'});
});