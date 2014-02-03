$(document).ready(function() {

    $("a[id^=swat-player-button]").click(function() {
        $("#swat-player-uuid").val($(this).data("uuid"));
        var msg = "Bribe police to SWAT player for $" + $(this).data("price") + "?";
        $("#swat-player-description").text(msg);
    });

    $("#swat-player-submit").click(function() {
        $("#swat-player-form").submit();
    });

});