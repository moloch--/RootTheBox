$(document).ready(function() {

    $("#start-game-button").click(function() {
        $("#start-game").val("true");
        $("#start-game-form").submit();
    });

    $("#stop-game-button").click(function() {
        $("#start-game").val("false");
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