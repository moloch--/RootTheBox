$(document).ready(function() {

    $("a[id^='buy-source-code-button']").click(function() {
        $("#buy-source-code-uuid").val($(this).data("uuid"));
        $("#buy-source-code-dialog").text(
            "Are you sure you want to buy this code for " + $(this).data("price") + "?"
        );
    });

    $("#buy-source-code-submit").click(function() {
        $("#buy-source-code-form").submit();
    });

    $("a[id^='download-source-code-button']").click(function() {
        window.open('/source_code_market/download?uuid=' + $(this).data("uuid"), '_newtab');
    });

});
