$(document).ready(function() {

    /* Flags */
    $("a[id^=capture-file-flag-button]").click(function() {
        $("#capture-file-flag-uuid").val($(this).data("uuid"));
    });

    $("#capture-file-flag-submit").click(function() {
        $("#capture-file-flag-form").submit();
    });

    $("a[id^=capture-text-flag-button]").click(function() {
        $("#capture-text-flag-uuid").val($(this).data("uuid"));
    });

    $("#capture-text-flag-submit").click(function() {
        $("#capture-text-flag-form").submit();
    });

    $("a[id^=capture-choice-flag-button]").click(function() {
        $("#capture-choice-flag-uuid").val($(this).data("uuid"));
        $("#choiceinput").empty();
        var choices = $(this).data("choices");
        for (choice in choices) {
            $("#choiceinput").append('<div><input required name="multichoice" type="radio" style="margin-top: 0;" value="' + choices[choice] + '" />&nbsp;&nbsp;' + choices[choice] + "</div><br/>");
        }
    });

    $("#capture-choice-flag-submit").click(function() {
        $("#choice-flag-token").val($('input[name=multichoice]:checked').val());
        $("#capture-choice-flag-form").submit();
    });

    /* Hints */
    $("a[id^=purchase-hint-button]").click(function() { 
        $("#purchase-hint-uuid").val($(this).data("uuid"));
        var price = $(this).data("price");
        hintdialog(price);
    });
    $("a[id^=purchase-flag-hint-button]").click(function() {
        //index is different on flags
        $("#purchase-hint-uuid").val($(this).data("uuid"));
        var price = $(this).data("price");
        hintdialog(price);
    });
    $("#purchase-hint-submit").click(function() {
        $("#purchase-hint-form").submit();
    });

    function hintdialog(price) {
        var bank = $("#hintbanking").val();
        if (price === "0") {
            $("#purchase-hint-text").text("This hint is free.  Would you like to take it?");
        } else if (bank == 'true') {
            $("#purchase-hint-text").text("Would you like to purchase this hint for $"+price+"?");
        } else {
            $("#purchase-hint-text").text("Would you like to take this hint for a deduction of "+price+" points?");
        }
    }
    $('td').on('mouseenter mouseleave', function(e) {
        //Allows the hover background to include the flag hints
        var tbody = $(this).closest("tbody");
        if (tbody.hasClass("flagbody")) {
            if ($(this).hasClass("successcol")) {
                tbody.css('background-color', $(this).next().css('background-color'));
            } else {
                tbody.css('background-color', $(this).css('background-color'));
            }
        }
    });
    $('tbody').on('mouseleave', function(e) {
        $(this).css('background-color','');
    });
});
