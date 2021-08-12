$(document).ready(function() {

    /* Category Item */
    $("a[id^=edit-category-item-button]").click(function() {
        $("#edit-category-item-uuid").val($(this).data("uuid"));
        $("#edit-category-item-name").val($(this).data("name"));
        $("#edit-category-description").val($(this).data("description"));
    });

    $("#edit-category-item-submit").click(function() {
        $("#edit-category-item-form").submit();
    });

    $("a[id^=delete-category-button]").click(function() {
        $("#delete-category-uuid").val($(this).data("uuid"));
    });

    $("#delete-category-submit").click(function() {
        $("#delete-category-form").submit();
    });

});