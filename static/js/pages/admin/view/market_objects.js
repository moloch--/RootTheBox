$(document).ready(function() {

    /* Market Item */
    $("a[id^=edit-market-item-button]").click(function() {
        $("#edit-market-item-uuid").val($(this).data("uuid"));
        $("#edit-market-item-price").val($(this).data("price"));
    });

    $("#edit-market-item-submit").click(function() {
        $("#edit-market-item-form").submit();
    });

});