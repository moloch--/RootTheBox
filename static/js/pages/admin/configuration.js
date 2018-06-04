$(document).ready(function() {

    /* Disable & Hide fields if their corisponding features are disabled */
    if ($("#use-bots").val() === "false") {
        $('#bot-grouping').hide();
        $('#bot-reward').prop('disabled', true);
    }
    if ($("#use-black-market").val() === "false") {
        $('#blackmarket-grouping').hide();
        $('#password-upgrade-cost').prop('disabled', true);
        $('#bribe-cost').prop('disabled', true);
    }
    if ($("#teams").val() === "false") {
        $("#team-grouping").hide();
        $("#max-team-size").prop('disabled', true);
        $("#max-pastebin-size").prop('disabled', true);
    }
    if ($("#banking").val() === "false") {
        $("#bank-grouping").hide();
        $("#max-password-length").prop('disabled', true);
    }

    /* Set initial state for buttons */
    if ($("#restrict-registration").val() === "true") {
        $("#restrict-registration-enable-icon").removeClass("fa-square-o");
        $("#restrict-registration-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#restrict-registration-disable-icon").removeClass("fa-square-o");
        $("#restrict-registration-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#hints-taken").val() === "true") {
        $("#hints-taken-enable-icon").removeClass("fa-square-o");
        $("#hints-taken-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#hints-taken-disable-icon").removeClass("fa-square-o");
        $("#hints-taken-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#teams").val() === "true") {
        $("#teams-enable-icon").removeClass("fa-square-o");
        $("#teams-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#teams-disable-icon").removeClass("fa-square-o");
        $("#teams-disable-icon").addClass("fa-check-square-o");
    }
    
    if ($("#public-teams").val() === "true") {
        $("#public-teams-enable-icon").removeClass("fa-square-o");
        $("#public-teams-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#public-teams-disable-icon").removeClass("fa-square-o");
        $("#public-teams-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#banking").val() === "true") {
        $("#banking-enable-icon").removeClass("fa-square-o");
        $("#banking-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#banking-disable-icon").removeClass("fa-square-o");
        $("#banking-disable-icon").addClass("fa-check-square-o");
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

    $("#hints-taken-enable").click(function() {
        $("#hints-taken").val("true");
        $("#hints-taken-enable-icon").removeClass("fa-square-o");
        $("#hints-taken-enable-icon").addClass("fa-check-square-o");
        $("#hints-taken-disable-icon").removeClass("fa-check-square-o");
        $("#hints-taken-disable-icon").addClass("fa-square-o");
    });
    $("#hints-taken-disable").click(function() {
        $("#hints-taken").val("false");
        $("#hints-taken-disable-icon").removeClass("fa-square-o");
        $("#hints-taken-disable-icon").addClass("fa-check-square-o");
        $("#hints-taken-enable-icon").removeClass("fa-check-square-o");
        $("#hints-taken-enable-icon").addClass("fa-square-o");
    });

    $("#teams-enable").click(function() {
        $("#teams").val("true");
        $("#teams-enable-icon").removeClass("fa-square-o");
        $("#teams-enable-icon").addClass("fa-check-square-o");
        $("#teams-disable-icon").removeClass("fa-check-square-o");
        $("#teams-disable-icon").addClass("fa-square-o");
        $("#max-team-size").prop('disabled', false);
        $("#max-pastebin-size").prop('disabled', false);
        $("#public-teams-enable").click();
        $("#team-grouping").slideDown();
    });
    $("#teams-disable").click(function() {
        $("#teams").val("false");
        $("#teams-disable-icon").removeClass("fa-square-o");
        $("#teams-disable-icon").addClass("fa-check-square-o");
        $("#teams-enable-icon").removeClass("fa-check-square-o");
        $("#teams-enable-icon").addClass("fa-square-o");
        $("#public-teams-disable").click();
        $("#max-team-size").prop('disabled', true);
        $("#max-pastebin-size").prop('disabled', true);
        $("#team-grouping").slideUp();
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

    $("#banking-enable").click(function() {
        $("#banking").val("true");
        $("#moneyname").text("Money");
        $("#banking-enable-icon").removeClass("fa-square-o");
        $("#banking-enable-icon").addClass("fa-check-square-o");
        $("#banking-disable-icon").removeClass("fa-check-square-o");
        $("#banking-disable-icon").addClass("fa-square-o");
        $("#max-password-length").prop('disabled', false);
        $("#bank-grouping").slideDown();
    });
    $("#banking-disable").click(function() {
        $("#banking").val("false");
        $("#moneyname").text("Score");
        $("#banking-disable-icon").removeClass("fa-square-o");
        $("#banking-disable-icon").addClass("fa-check-square-o");
        $("#banking-enable-icon").removeClass("fa-check-square-o");
        $("#banking-enable-icon").addClass("fa-square-o");
        $("#banking-teams-disable").click();
        $("#max-password-length").prop('disabled', true);
        $("#bank-grouping").slideUp();
    });


    $("#use-bots-enable").click(function() {
        $("#use-bots").val("true");
        $("#use-bots-enable-icon").removeClass("fa-square-o");
        $("#use-bots-enable-icon").addClass("fa-check-square-o");
        $("#use-bots-disable-icon").removeClass("fa-check-square-o");
        $("#use-bots-disable-icon").addClass("fa-square-o");
        $('#bot-reward').prop('disabled', false);
        $('#bot-grouping').slideDown();
    });
    $("#use-bots-disable").click(function() {
        $("#use-bots").val("false");
        $("#use-bots-disable-icon").removeClass("fa-square-o");
        $("#use-bots-disable-icon").addClass("fa-check-square-o");
        $("#use-bots-enable-icon").removeClass("fa-check-square-o");
        $("#use-bots-enable-icon").addClass("fa-square-o");
        $('#bot-reward').prop('disabled', true);
        $('#bot-grouping').slideUp();
    });

    $("#use-black-market-enable").click(function() {
        $("#use-black-market").val("true");
        $("#use-black-market-enable-icon").removeClass("fa-square-o");
        $("#use-black-market-enable-icon").addClass("fa-check-square-o");
        $("#use-black-market-disable-icon").removeClass("fa-check-square-o");
        $("#use-black-market-disable-icon").addClass("fa-square-o");
        $('#password-upgrade-cost').prop('disabled', false);
        $('#bribe-cost').prop('disabled', false);
        $('#blackmarket-grouping').slideDown();
    });
    $("#use-black-market-disable").click(function() {
        $("#use-black-market").val("false");
        $("#use-black-market-disable-icon").removeClass("fa-square-o");
        $("#use-black-market-disable-icon").addClass("fa-check-square-o");
        $("#use-black-market-enable-icon").removeClass("fa-check-square-o");
        $("#use-black-market-enable-icon").addClass("fa-square-o");
        $('#password-upgrade-cost').prop('disabled', true);
        $('#bribe-cost').prop('disabled', true);
        $('#blackmarket-grouping').slideUp();
    });

    /* Enable popovers */
    $("#game-name").popover({placement:'right', trigger:'hover'});
    $("#restrict-registration-button").popover({placement:'right', trigger:'hover'});
    $("#public-teams-button").popover({placement:'right', trigger:'hover'});
    $("#hints-taken-button").popover({placement:'right', trigger:'hover'});
    $("#teams-button").popover({placement:'right', trigger:'hover'});
    $("#max-team-size").popover({placement:'right', trigger:'hover'});
    $("#min-user-password-length").popover({placement:'right', trigger:'hover'});
    $("#banking-button").popover({placement:'right', trigger:'hover'});
    $("#max-password-length").popover({placement:'right', trigger:'hover'});
    $("#use-bots-button").popover({placement:'right', trigger:'hover'});
    $("#bot-reward").popover({placement:'right', trigger:'hover'});
    $("#use-black-market-button").popover({placement:'right', trigger:'hover'});
    $("#password-upgrade-cost").popover({placement:'right', trigger:'hover'});
    $("#bribe-cost").popover({placement:'right', trigger:'hover'});
});