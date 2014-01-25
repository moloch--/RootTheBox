$(document).ready(function() {
    if ($("#logout").length) {
        $("#logout").click(function() {
            $("#logout-form").submit();
        });
    }
});
