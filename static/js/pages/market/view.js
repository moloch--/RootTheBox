$(document).ready(function() {

    $("a[id^=item-details-button]").click(function() {
        var uuid = $(this).data("uuid");
        $("#buy-market-item-uuid").val(uuid);
        $.getJSON('/user/market/details?uuid=' + uuid, function(data) {
            $.each(data, function(key, val) {
                //console.log("#" + key.toString() + " -> " + val.toString());
                if (key !== "image") {
                    $("#" + key).text(val);
                } else {
                    $("#image").attr("src", function() {
                        return "/static/images/" + val;
                    });
                }
            });
        });
    });

    $("#buy-market-item-submit").click(function() {
        $("#buy-market-item-form").submit();
    });

});