$(document).ready(function() {

    /* Popovers */
    $("#flag-name").popover({placement:'right', trigger:'hover'});
    $("#token").popover({placement:'right', trigger:'hover'});
    $("#description").popover({placement:'right', trigger:'hover'});
    $("#capture-message").popover({placement:'right', trigger:'hover'});
    $("#reward").popover({placement:'right', trigger:'hover'});
    $("#box-uuid").popover({placement:'right', trigger:'hover'});
    $("#case-button").popover({placement:'right', trigger:'hover'});

    $("#case-enable").click(function() {
        $("#case-sensitve").val(1);
        $("#case-enable-icon").removeClass("fa-square-o");
        $("#case-enable-icon").addClass("fa-check-square-o");
        $("#case-disable-icon").removeClass("fa-check-square-o");
        $("#case-disable-icon").addClass("fa-square-o");
    });
    $("#case-disable").click(function() {
        $("#case-sensitive").val(0);
        $("#case-disable-icon").removeClass("fa-square-o");
        $("#case-disable-icon").addClass("fa-check-square-o");
        $("#case-enable-icon").removeClass("fa-check-square-o");
        $("#case-enable-icon").addClass("fa-square-o");
    });
});