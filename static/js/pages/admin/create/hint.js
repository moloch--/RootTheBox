$(document).ready(function() {
    /* markdown */
    $(function () {
        $('[data-toggle="tooltip"]').tooltip();
        $('.toolbar').markdownToolbar(false);
    })

    /* Popovers */
    $("#price").popover({placement:'right', trigger:'hover'});
    $("#description").popover({placement:'right', trigger:'hover'});

});