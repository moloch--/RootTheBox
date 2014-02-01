$(document).ready(function() {

    $("a[id^=unlock-game-level-button]").click(function() {
        var buyout = $(this).data("buyout");
        $("#unlock-game-level-uuid").val($(this).data("uuid"));
        $("#description").text("Would you like to unlock this level for $"+buyout+"?");
    });

    $("#unlock-game-level-submit").click(function() {
        $("#unlock-game-level-form").submit();
    });

});