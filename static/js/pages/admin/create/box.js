$(document).ready(function() {

    /* Button callbacks */
    $("button[id^=os-button]").click(function() {
        $("#operating-system").val($(this).data("os"));
    });

    $("#autoformat-enable").click(function() {
        $("#autoformat").val("true");
        $("#autoformat-enable-icon").removeClass("fa-square-o");
        $("#autoformat-enable-icon").addClass("fa-check-square-o");
        $("#autoformat-disable-icon").removeClass("fa-check-square-o");
        $("#autoformat-disable-icon").addClass("fa-square-o");
    });
    $("#autoformat-disable").click(function() {
        $("#autoformat").val("false");
        $("#autoformat-disable-icon").removeClass("fa-square-o");
        $("#autoformat-disable-icon").addClass("fa-check-square-o");
        $("#autoformat-enable-icon").removeClass("fa-check-square-o");
        $("#autoformat-enable-icon").addClass("fa-square-o");
    });

    /* Popovers */
    $("#autoformat-button").popover({placement:'right', trigger:'hover'});
});