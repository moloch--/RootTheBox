$(document).ready(function() {

    $("a[id^=delete-token-button]").click(function() {
        $("#token-value").val($(this).data("value"));
        $("#token-form").submit();
    });

});