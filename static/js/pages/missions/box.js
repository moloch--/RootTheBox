$(document).ready(function() {

    /* Flags */
    $("a[id^=capture-file-flag-button]").click(function() {
        $("#capture-file-flag-uuid").val($(this).data("uuid"));
    });

    $("#capture-file-flag-submit").click(function() {
        $("#capture-file-flag-form").submit();
    });

    $("a[id^=capture-text-flag-button]").click(function() {
        $("#capture-text-flag-uuid").val($(this).data("uuid"));
    });

    $("#capture-text-flag-submit").click(function() {
        $("#capture-text-flag-form").submit();
    });

    /* Hints */
    $("a[id^=purchase-hint-button]").click(function() { 
        $("#purchase-hint-uuid").val($(this).data("uuid"));
        var price = $(this).data("price");
        hintdialog(price);
    });
    $("a[id^=purchase-flag-hint-button]").click(function() {
        //index is different on flags
        $("#purchase-hint-uuid").val($(this).data("uuid"));
        var price = $(this).data("price");
        hintdialog(price);
    });
    $("#purchase-hint-submit").click(function() {
        $("#purchase-hint-form").submit();
    });

    function hintdialog(price) {
        var bank = $("#hintbanking").val();
        if (price === "0") {
            $("#purchase-hint-text").text("This hint is free.  Would you like to take it?");
        } else if (bank == 'true') {
            $("#purchase-hint-text").text("Would you like to purchase this hint for $"+price+"?");
        } else {
            $("#purchase-hint-text").text("Would you like to take this hint for a deduction of "+price+" points?");
        }
    }

});
