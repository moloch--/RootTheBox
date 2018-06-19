$(document).ready(function() {

    /* Category Item */
    $("a[id^=edit-category-item-button]").click(function() {
        $("#edit-category-item-uuid").val($(this).data("uuid"));
        $("#edit-category-item-name").val($(this).data("name"));
    });

    $("#edit-category-item-submit").click(function() {
        $("#edit-category-item-form").submit();
    });

});