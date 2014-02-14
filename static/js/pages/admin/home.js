$(document).ready(function() {

    $("#start-game-button").click(function() {
        $("#start-game").val("true");
        $("#start-game-form").submit();
    });

    $("#stop-game-button").click(function() {
        $("#start-game").val("false");
        $("#start-game-form").submit();
    });

});