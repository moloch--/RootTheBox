function penalty_cost_update() {
    var stop_penalty = parseInt($("#flag_stop_penalty").val());
    var start_penalty = parseInt($("#flag_start_penalty").val());
    if (stop_penalty <= start_penalty) {
        $("#flag_stop_penalty").val(start_penalty + 1);
        stop_penalty = parseInt($("#flag_stop_penalty").val());
    }
    var max_cost = (stop_penalty - start_penalty) * parseInt($("#flag_penalty_cost").val());
    $("#current_max_penalty").text($("#penalty_description").data("maxpenalty") + 
        ": " + max_cost + "% " + $("#penalty_description").data("flagvalue"));
    var penalty_attempt = "s " + start_penalty + " – " + (stop_penalty - 1);
    if (start_penalty == (stop_penalty - 1)) {
        penalty_attempt = " " + start_penalty;
    }
    $("#penalty_description").text($("#penalty_description").data("applytext") + penalty_attempt);
}

$(document).ready(function() {
    penalty_cost_update();

    /* Hide fields if their corresponding features are disabled */
    if ($("#use-bots").val() === "false") {
        $('#bot-grouping').hide();
    }
    if ($("#use-black-market").val() === "false") {
        $('#blackmarket-grouping').hide();
    }
    if ($("#require-email").val() === "false") {
        $("#email-grouping").hide();
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
    if ($("#team-sharing").val() == "false") {
        $("#teamshare-grouping").hide();
    }
    if ($("#show-mvp").val() == "false") {
        $("#mvp-grouping").hide();
    }

    /* Set initial state for buttons */
    if ($("#require-email").val() === "true") {
        $("#require-email-enable-icon").removeClass("fa-square-o");
        $("#require-email-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#require-email-disable-icon").removeClass("fa-square-o");
        $("#require-email-disable-icon").addClass("fa-check-square-o");
    }
    
    if ($("#validate-email").val() === "true") {
        $("#validate-email-enable-icon").removeClass("fa-square-o");
        $("#validate-email-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#validate-email-disable-icon").removeClass("fa-square-o");
        $("#validate-email-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#restrict-registration").val() === "true") {
        $("#restrict-registration-enable-icon").removeClass("fa-square-o");
        $("#restrict-registration-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#restrict-registration-disable-icon").removeClass("fa-square-o");
        $("#restrict-registration-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#global-notifications").val() === "true") {
        $("#global-notifications-enable-icon").removeClass("fa-square-o");
        $("#global-notifications-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#global-notifications-disable-icon").removeClass("fa-square-o");
        $("#global-notifications-disable-icon").addClass("fa-check-square-o");
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

    if ($("#show-mvp").val() === "true") {
        $("#show-mvp-enable-icon").removeClass("fa-square-o");
        $("#show-mvp-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#show-mvp-disable-icon").removeClass("fa-square-o");
        $("#show-mvp-disable-icon").addClass("fa-check-square-o");
    }

    if ($("#team-sharing").val() === "true") {
        $("#team-sharing-enable-icon").removeClass("fa-square-o");
        $("#team-sharing-enable-icon").addClass("fa-check-square-o");
    } else {
        $("#team-sharing-disable-icon").removeClass("fa-square-o");
        $("#team-sharing-disable-icon").addClass("fa-check-square-o");
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
    
    if ($("#story_mode").val() === "true") {
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
    $("#require-email-enable").click(function() {
        $("#require-email").val("true");
        $("#require-email-enable-icon").removeClass("fa-square-o");
        $("#require-email-enable-icon").addClass("fa-check-square-o");
        $("#require-email-disable-icon").removeClass("fa-check-square-o");
        $("#require-email-disable-icon").addClass("fa-square-o");
        $("#email-grouping").slideDown();
    });
    $("#require-email-disable").click(function() {
        $("#require-email").val("false");
        $("#require-email-disable-icon").removeClass("fa-square-o");
        $("#require-email-disable-icon").addClass("fa-check-square-o");
        $("#require-email-enable-icon").removeClass("fa-check-square-o");
        $("#require-email-enable-icon").addClass("fa-square-o");
        $("#email-grouping").slideUp();
    });
    $("#validate-email-enable").click(function() {
        $("#validate-email").val("true");
        $("#validate-email-enable-icon").removeClass("fa-square-o");
        $("#validate-email-enable-icon").addClass("fa-check-square-o");
        $("#validate-email-disable-icon").removeClass("fa-check-square-o");
        $("#validate-email-disable-icon").addClass("fa-square-o");
    });
    $("#validate-email-disable").click(function() {
        $("#validate-email").val("false");
        $("#validate-email-disable-icon").removeClass("fa-square-o");
        $("#validate-email-disable-icon").addClass("fa-check-square-o");
        $("#validate-email-enable-icon").removeClass("fa-check-square-o");
        $("#validate-email-enable-icon").addClass("fa-square-o");
    });
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

    $("#global-notifications-enable").click(function() {
        $("#global-notifications").val("true");
        $("#global-notifications-enable-icon").removeClass("fa-square-o");
        $("#global-notifications-enable-icon").addClass("fa-check-square-o");
        $("#global-notifications-disable-icon").removeClass("fa-check-square-o");
        $("#global-notifications-disable-icon").addClass("fa-square-o");
        $('#global-notifications-grouping').slideDown();
    });
    $("#global-notifications-disable").click(function() {
        $("#global-notifications").val("false");
        $("#global-notifications-disable-icon").removeClass("fa-square-o");
        $("#global-notifications-disable-icon").addClass("fa-check-square-o");
        $("#global-notifications-enable-icon").removeClass("fa-check-square-o");
        $("#global-notifications-enable-icon").addClass("fa-square-o");
        $('#global-notifications-grouping').slideUp();
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

    $("#show-mvp-enable").click(function() {
        $("#show-mvp").val("true");
        $("#show-mvp-enable-icon").removeClass("fa-square-o");
        $("#show-mvp-enable-icon").addClass("fa-check-square-o");
        $("#show-mvp-disable-icon").removeClass("fa-check-square-o");
        $("#show-mvp-disable-icon").addClass("fa-square-o");
        $("#mvp-grouping").slideDown();
    });
    $("#show-mvp-disable").click(function() {
        $("#show-mvp").val("false");
        $("#show-mvp-disable-icon").removeClass("fa-square-o");
        $("#show-mvp-disable-icon").addClass("fa-check-square-o");
        $("#show-mvp-enable-icon").removeClass("fa-check-square-o");
        $("#show-mvp-enable-icon").addClass("fa-square-o");
        $("#mvp-grouping").slideUp();
    });

    $("#team-sharing-enable").click(function() {
        $("#team-sharing").val("true");
        $("#team-sharing-enable-icon").removeClass("fa-square-o");
        $("#team-sharing-enable-icon").addClass("fa-check-square-o");
        $("#team-sharing-disable-icon").removeClass("fa-check-square-o");
        $("#team-sharing-disable-icon").addClass("fa-square-o");
        $("#teamshare-grouping").slideDown();
    });
    $("#team-sharing-disable").click(function() {
        $("#team-sharing").val("false");
        $("#team-sharing-disable-icon").removeClass("fa-square-o");
        $("#team-sharing-disable-icon").addClass("fa-check-square-o");
        $("#team-sharing-enable-icon").removeClass("fa-check-square-o");
        $("#team-sharing-enable-icon").addClass("fa-square-o");
        $("#teamshare-grouping").slideUp();
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
        $("#story_mode").val("true");
        $("#story-enable-icon").removeClass("fa-square-o");
        $("#story-enable-icon").addClass("fa-check-square-o");
        $("#story-disable-icon").removeClass("fa-check-square-o");
        $("#story-disable-icon").addClass("fa-square-o");
    });
    $("#story-disable").click(function() {
        $("#story_mode").val("false");
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

    $(".penaltyval").change(function() {
        penalty_cost_update();
    });

    /* Enable popovers */
    $("#game-name").popover({placement:'right', trigger:'hover'});
    $("#require-email-button").popover({placement:'right', trigger:'hover'});
    $("#validate-email-button").popover({placement:'right', trigger:'hover'});
    $("#restrict-registration-button").popover({placement:'right', trigger:'hover'});
    $("#global-notifications-button").popover({placement:'right', trigger:'hover'});
    $("#public-teams-button").popover({placement:'right', trigger:'hover'});
    $("#show-mvp-button").popover({placement:'right', trigger:'hover'});
    $("#mvp-max").popover({placement:'right', trigger:'hover'});
    $("#team-sharing-button").popover({placement:'right', trigger:'hover'});
    $("#hints-taken-button").popover({placement:'right', trigger:'hover'});
    $("#teams-button").popover({placement:'right', trigger:'hover'});
    $("#max-team-size").popover({placement:'right', trigger:'hover'});
    $("#min-user-password-length").popover({placement:'right', trigger:'hover'});
    $("#max-flag-attempts").popover({placement:'right', trigger:'hover'});
    $("#dynamic_flag-button").popover({placement:'right', trigger:'hover'});
    $("#dynamic_flag_type").popover({placement:'right', trigger:'hover'});
    $("#flag_value_decrease").popover({placement:'right', trigger:'hover'});
    $("#flag_value_minimum").popover({placement:'right', trigger:'hover'});
    $("#penalty-button").popover({placement:'right', trigger:'hover'});
    $("#flag_start_penalty").popover({placement:'right', trigger:'hover'});
    $("#flag_penalty_cost").popover({placement:'right', trigger:'hover'});
    $("#flag_stop_penalty").popover({placement:'right', trigger:'hover'});
    $("#banking-button").popover({placement:'right', trigger:'hover'});
    $("#story-button").popover({placement:'right', trigger:'hover'});
    $("#rank_by").popover({placement:'right', trigger:'hover'});
    $("#scoreboard_visibility").popover({placement:'right', trigger:'hover'});
    $("#max-password-length").popover({placement:'right', trigger:'hover'});
    $("#starting-team-money").popover({placement:'right', trigger:'hover'});
    $("#use-bots-button").popover({placement:'right', trigger:'hover'});
    $("#bot-reward").popover({placement:'right', trigger:'hover'});
    $("#use-black-market-button").popover({placement:'right', trigger:'hover'});
    $("#password-upgrade-cost").popover({placement:'right', trigger:'hover'});
    $("#bribe-cost").popover({placement:'right', trigger:'hover'});
});