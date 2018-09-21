function getDetails(obj, uuid) {
    $("#details-" + obj + "-uuid").val(uuid);
    data = {'uuid': uuid, 'obj': "stats", '_xsrf': getCookie("_xsrf")};
    $.post('/admin/ajax/objects', data, function(response) {
        $.each(response, function(key, value) {
            $("#details-" + key).empty();
            $("#details-" + key).append(function() {
                var table = ""
                if (value.length > 0) {
                    for (i=0; i < value.length; i++) {
                        table += "<tr><td style='text-align: center; width: 33%;'>" + value[i].name + "</td>";
                        if (value[i].token !== undefined) {
                            table += "<td style='text-align: center; width: 33%;'>" + value[i].token + "</td>";
                        }
                        if (value[i].price !== undefined) {
                            table += "<td style='text-align: center; width: 33%;'>" + value[i].price + "</td>";
                        }
                        table += "</tr>"
                    }
                } else {
                    table = "None"
                }
                return table;
            });
        });
    }, 'json');
}

/* Add click events */
$(document).ready(function() {

    /* Flag Details */
    $("a[id^=details-flag-button]").click(function() {
        getDetails("flag", $(this).data("uuid"));
    });

});