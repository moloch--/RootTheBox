$(document).ready(function() {
    barcolor();
});

function barcolor() {
    $("a[id^=unlock-game-level-button]").click(function() {
        var buyout = $(this).data("buyout");
        var banking = $(this).data("banking");
        $("#unlock-game-level-uuid").val($(this).data("uuid"));
        var description = "Would you like to unlock this level for ";
        if (banking) {
            description += "$" + buyout + "?";
        } else {
            description += buyout + " point(s)";
        }
        $("#description").text(description);
    });

    $("#unlock-game-level-submit").click(function() {
        $("#unlock-game-level-form").submit();
    });
    
    $(".minibar").each(function() {
        if (this.style.width == "100%") {
            $(this).css('background-color', "#00bb00");
            $(this).css('background-image', 'linear-gradient(to bottom,#00bb00,#009900)')
        } else {
            $(this).css('background-color', "#eeee00");
            $(this).css('background-image', 'linear-gradient(to bottom,#eeee00,#b3b300)');
        }
    });
}