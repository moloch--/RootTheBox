
function penalty_cost_update() {
    var max_cost = ($("#flag_stop_penalty").val() - $("#flag_start_penalty").val()) * $("#flag_penalty_cost").val();
    $("#flag_start_penalty").attr('data-content', "When to start applying the penalty.  For example, you may want the first incorrect attempt to be free, but penalize subsequent attempts.<br/><br/>1 = deduct on & after 1st attempt<br/>2 = deduct on & after 2nd attempt<br/>and so on ...<br/><br/>Maxium Penalty is determined as<br/>(stop - start) * cost.<br/><strong>Current Max Penalty: " + max_cost + "%</strong>");
    $("#flag_stop_penalty").attr('data-content', "When to stop applying the penalty.  For example, you may want to only penalize a certain total of the flags value and allow any further attempts to be free, thus allowing all flags to have some value.<br/><br/>4 = stop on & after 4th attempt<br/>5 = stop on & after 5th attempt<br/>and so on ...<br/><br/>Maxium Penalty is determined as<br/>(stop - start) * cost.<br/><strong>Current Max Penalty: " + max_cost + "%</strong>");
    $("#flag_penalty_cost").attr('data-content', "Penalize the score by this percent of the flag value for each incorrect attempt (applied after dynamic scoring if enabled).<br/><br/>Maxium Penalty is determined as<br/>(stop - start) * cost.<br/><strong>Current Max Penalty: " + max_cost + "%</strong>");
}

$(document).ready(function() {
    penalty_cost_update();

    /* Hide fields if their corisponding features are disabled */
    if ($("#use-bots").val() === "false") {
        $('#bot-grouping').hide();
    }
    if ($("#use-black-market").val() === "false") {
        $('#blackmarket-grouping').hide();
    }
    if ($("#teams").val() === "false") {
        $("#team-grouping").hide();
    }
    if ($("#banking").val() === "false") {
        $("#bank-grouping").hide();
    }
    if ($("#dynamic_flag_value").val() == "false") {
        $("#dynamic_flag-grouping").hide();
    }
    if ($("#penalize_flag_value").val() == "false") {
        $("#penalty-grouping").hide();
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

    if ($("#dynamic_flag_value").val() === "true") {
        $("#dynamic_flag-enable-icon").removeClass("fa-square-o");
        $("#dynamic_flag-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#dynamic_flag-disable-icon").removeClass("fa-square-o");
        $("#dynamic_flag-disable-icon").addClass("fa-check-square-o");
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
    
    if ($("#secure_communique_dialog").val() === "true") {
        $("#story-enable-icon").removeClass("fa-square-o");
        $("#story-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#story-disable-icon").removeClass("fa-square-o");
        $("#story-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#penalize_flag_value").val() === "true") {
        $("#penalty-enable-icon").removeClass("fa-square-o");
        $("#penalty-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#penalty-disable-icon").removeClass("fa-square-o");
        $("#penalty-disable-icon").addClass("fa-check-square-o");
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
        $("#bank-grouping").slideDown();
    });
    $("#banking-disable").click(function() {
        $("#banking").val("false");
        $("#moneyname").text("Points");
        $("#banking-disable-icon").removeClass("fa-square-o");
        $("#banking-disable-icon").addClass("fa-check-square-o");
        $("#banking-enable-icon").removeClass("fa-check-square-o");
        $("#banking-enable-icon").addClass("fa-square-o");
        $("#banking-teams-disable").click();
        $("#bank-grouping").slideUp();
    });


    $("#use-bots-enable").click(function() {
        $("#use-bots").val("true");
        $("#use-bots-enable-icon").removeClass("fa-square-o");
        $("#use-bots-enable-icon").addClass("fa-check-square-o");
        $("#use-bots-disable-icon").removeClass("fa-check-square-o");
        $("#use-bots-disable-icon").addClass("fa-square-o");
        $('#bot-grouping').slideDown();
    });
    $("#use-bots-disable").click(function() {
        $("#use-bots").val("false");
        $("#use-bots-disable-icon").removeClass("fa-square-o");
        $("#use-bots-disable-icon").addClass("fa-check-square-o");
        $("#use-bots-enable-icon").removeClass("fa-check-square-o");
        $("#use-bots-enable-icon").addClass("fa-square-o");
        $('#bot-grouping').slideUp();
    });

    $("#use-black-market-enable").click(function() {
        $("#use-black-market").val("true");
        $("#use-black-market-enable-icon").removeClass("fa-square-o");
        $("#use-black-market-enable-icon").addClass("fa-check-square-o");
        $("#use-black-market-disable-icon").removeClass("fa-check-square-o");
        $("#use-black-market-disable-icon").addClass("fa-square-o");
        $('#blackmarket-grouping').slideDown();
    });
    $("#use-black-market-disable").click(function() {
        $("#use-black-market").val("false");
        $("#use-black-market-disable-icon").removeClass("fa-square-o");
        $("#use-black-market-disable-icon").addClass("fa-check-square-o");
        $("#use-black-market-enable-icon").removeClass("fa-check-square-o");
        $("#use-black-market-enable-icon").addClass("fa-square-o");
        $('#blackmarket-grouping').slideUp();
    });

    $("#dynamic_flag-enable").click(function() {
        $("#dynamic_flag_value").val("true");
        $("#dynamic_flag-enable-icon").removeClass("fa-square-o");
        $("#dynamic_flag-enable-icon").addClass("fa-check-square-o");
        $("#dynamic_flag-disable-icon").removeClass("fa-check-square-o");
        $("#dynamic_flag-disable-icon").addClass("fa-square-o");
        $('#dynamic_flag-grouping').slideDown();
    });
    $("#dynamic_flag-disable").click(function() {
        $("#dynamic_flag_value").val("false");
        $("#dynamic_flag-disable-icon").removeClass("fa-square-o");
        $("#dynamic_flag-disable-icon").addClass("fa-check-square-o");
        $("#dynamic_flag-enable-icon").removeClass("fa-check-square-o");
        $("#dynamic_flag-enable-icon").addClass("fa-square-o");
        $('#dynamic_flag-grouping').slideUp();
    });

    $("#story-enable").click(function() {
        $("#secure_communique_dialog").val("true");
        $("#story-enable-icon").removeClass("fa-square-o");
        $("#story-enable-icon").addClass("fa-check-square-o");
        $("#story-disable-icon").removeClass("fa-check-square-o");
        $("#story-disable-icon").addClass("fa-square-o");
    });
    $("#story-disable").click(function() {
        $("#secure_communique_dialog").val("false");
        $("#story-disable-icon").removeClass("fa-square-o");
        $("#story-disable-icon").addClass("fa-check-square-o");
        $("#story-enable-icon").removeClass("fa-check-square-o");
        $("#story-enable-icon").addClass("fa-square-o");
    });

    $("#penalty-enable").click(function() {
        $("#penalize_flag_value").val("true");
        $("#penalty-enable-icon").removeClass("fa-square-o");
        $("#penalty-enable-icon").addClass("fa-check-square-o");
        $("#penalty-disable-icon").removeClass("fa-check-square-o");
        $("#penalty-disable-icon").addClass("fa-square-o");
        $('#penalty-grouping').slideDown();
    });
    $("#penalty-disable").click(function() {
        $("#penalize_flag_value").val("false");
        $("#penalty-disable-icon").removeClass("fa-square-o");
        $("#penalty-disable-icon").addClass("fa-check-square-o");
        $("#penalty-enable-icon").removeClass("fa-check-square-o");
        $("#penalty-enable-icon").addClass("fa-square-o");
        $('#penalty-grouping').slideUp();
    });

    $( ".penaltyval" ).change(function() {
        penalty_cost_update();
    });

    /* Enable popovers */
    $("#game-name").popover({placement:'right', trigger:'hover'});
    $("#restrict-registration-button").popover({placement:'right', trigger:'hover'});
    $("#public-teams-button").popover({placement:'right', trigger:'hover'});
    $("#hints-taken-button").popover({placement:'right', trigger:'hover'});
    $("#teams-button").popover({placement:'right', trigger:'hover'});
    $("#max-team-size").popover({placement:'right', trigger:'hover'});
    $("#min-user-password-length").popover({placement:'right', trigger:'hover'});
    $("#dynamic_flag-button").popover({placement:'right', trigger:'hover'});
    $("#flag_value_decrease").popover({placement:'right', trigger:'hover'});
    $("#penalty-button").popover({placement:'right', trigger:'hover'});
    $("#flag_start_penalty").popover({placement:'right', trigger:'hover'});
    $("#flag_penalty_cost").popover({placement:'right', trigger:'hover'});
    $("#flag_stop_penalty").popover({placement:'right', trigger:'hover'});
    $("#banking-button").popover({placement:'right', trigger:'hover'});
    $("#story-button").popover({placement:'right', trigger:'hover'});
    $("#rank_by").popover({placement:'right', trigger:'hover'});
    $("#max-password-length").popover({placement:'right', trigger:'hover'});
    $("#use-bots-button").popover({placement:'right', trigger:'hover'});
    $("#bot-reward").popover({placement:'right', trigger:'hover'});
    $("#use-black-market-button").popover({placement:'right', trigger:'hover'});
    $("#password-upgrade-cost").popover({placement:'right', trigger:'hover'});
    $("#bribe-cost").popover({placement:'right', trigger:'hover'});
});