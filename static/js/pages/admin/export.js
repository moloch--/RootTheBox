$(document).ready(function() {

    $("#export-game-objects-button").click(function() {
        if ($("#game-objects").val() === "true") {
            $("#game-objects").val("false");
        } else {
            $("#game-objects").val("true");
        }
    });

    $("#export-users-button").click(function() {
        if ($("#users").val() === "true") {
            $("#users").val("false");
        } else {
            $("#users").val("true");
        }
    });

});