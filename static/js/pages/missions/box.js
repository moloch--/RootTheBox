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
        $("#purchase-hint-text").text("Would you like to purchase this hint for $"+price+"?");
    });

    $("#purchase-hint-submit").click(function() {
        $("#purchase-hint-form").submit();
    });

});
