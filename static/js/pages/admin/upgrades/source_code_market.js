$(document).ready(function() {

    $("a[id^=add-source-code-button]").click(function() {
        $("#add-source-code-uuid").val($(this).data("uuid"));
    });

    $("#add-source-code-submit").click(function() {
        $("#add-source-code-form").submit();
    });

    $("a[id^=delete-source-code-button]").click(function() {
        $("#delete-source-code-uuid").val($(this).data("uuid"));
    });

    $("#delete-source-code-submit").click(function() {
        $("#delete-source-code-form").submit();
    });

});