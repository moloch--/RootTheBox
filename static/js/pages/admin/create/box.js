$(document).ready(function() {

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

    /* Button callbacks */
    $(".osbutton").click(function() {
        $("#operating_system").val($(this).data("os"));
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

    $("#flag-submission-type-classic").click(function() {
        $("#flag_submission_type").val("CLASSIC");
        $("#flag-submission-type-classic-icon").removeClass("fa-square-o");
        $("#flag-submission-type-classic-icon").addClass("fa-check-square-o");
        $("#flag-submission-type-single-boxe-icon").removeClass("fa-check-square-o");
        $("#flag-submission-type-single-box-icon").addClass("fa-square-o");
    });
    $("#flag-submission-type-single-box").click(function() {
        $("#flag_submission_type").val("SINGLE_SUBMISSION_BOX");
        $("#flag-submission-type-classic-icon").removeClass("fa-check-square-o");
        $("#flag-submission-type-classic-icon").addClass("fa-square-o");
        $("#flag-submission-type-single-box-icon").removeClass("fa-square-o");
        $("#flag-submission-type-single-box-icon").addClass("fa-check-square-o");
    });

    /* Popovers */
    $("#box-name").popover({placement:'right', trigger:'hover'});
    $("#game-level").popover({placement:'right', trigger:'hover'});
    $("#corporation").popover({placement:'right', trigger:'hover'});
    $("#operating-system").popover({placement:'right', trigger:'hover'});
    $("#description").popover({placement:'right', trigger:'hover'});
    $("#autoformat-button").popover({placement:'right', trigger:'hover'});
    $("#flag-submission-type-button").popover({placement:'right', trigger:'hover'});
    $("#difficulty").popover({placement:'right', trigger:'hover'});

    /* Avatar */
    $(".boxavatarimg").click(function() {
        var filename = $(this).attr('value');
        $("#box_avatar_select").val(filename);
        $("#avatarfilename").text("File: " + filename.replace("box/",""));
        $("#avatarclose").click();
    });
    $("#box-avatar").change(function(){
        $("#avatarfilename").text("File: " + $(this).val());
        $("#box_avatar_select").val("");
    });

    $("#uploadbutton").click(function(){
        $("#box-avatar").click(); 
    });
    $("#removeavatar").click(function(){
        $("#avatarfilename").text("File: None");
        $("#box_avatar_select").val("none");
    });
});