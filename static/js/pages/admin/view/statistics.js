function getStatDetails(obj, uuid) {
    $("#details-" + obj + "-uuid").val(uuid);
    data = {'uuid': uuid, 'obj': "stats", '_xsrf': getCookie("_xsrf")};
    $.post('/admin/ajax/objects', data, function(response) {
        $.each(response, function(key, value) {
            if (key === "flag") {
                $("#flag_value").text(value[0]["price"]);
                $("#flag_value").text(value[0]["price"]);
                $("#details_flag_name").text(value[0].name);
                $("#details_flag_description").text(value[0].description);
                $("#details_flag_token").text(value[0].token);
                $("#count_attempts").text(response["attempts"].length);
                $("#count_captures").text(response["captures"].length);
                $("#count_hints").text(response["hints"].length);
            } else {
                $("#details-" + key).empty();
                $("#details-" + key).append(function() {
                    var table = "";
                    if (value.length > 0) {
                        for (i=0; i < value.length; i++) {
                            let tkn = $('<div>').html(value[i].token);
                            let nm = $('<div>').html(value[i].name);
                            table += "<tr><td class='shortcolumn statcolumn'>" + nm.text() + "</td>";
                            if (value[i].token !== undefined) {
                                table += "<td class='descriptioncol' style='text-align: center;'>" + tkn.text() + "</td>";
                            }
                            if (value[i].price !== undefined) {
                                table += "<td class='shortcolumn statcolumn'>" + value[i].price + "</td>";
                            }
                            if (value[i].penalty !== undefined) {
                                table += "<td class='shortcolumn statcolumn'>" + value[i].penalty + "</td>";
                            }
                            if (key == "attempts") {
                                table += "<td class='shortcolum statcolumn'><a class='acceptbtn btn btn-mini' href='#' ";
                                table += "data-flag-uuid='" + value[i].flag + "' data-team-uuid='" + value[i].team + "' ";
                                table += "data-team-name='" + nm.text() + "' data-flag-token='" + tkn.text() + "' ";
                                table += "data-flag-penalty='" + value[i].penalty + "' data-flag-type='" + value[i].type + "'>";
                                table += "Accept Answer</a></td>";
                            }
                            table += "</tr>";
                        }
                    } else {
                        table = "None";
                    }
                    return table;
                });
            }
            
            $('.acceptbtn').click(
                function(e) {
                    e.stopImmediatePropagation();
                    e.preventDefault();
                    resetAnswerModal();
                    $("#answer-team").text($(e.target).data("team-name"));
                    var token = $(e.target).data("flag-token");
                    var penalty = $(e.target).data("flag-penalty").replace("-$", "");
                    var flagtype = $(e.target).data("flag-type");
                    $("#answer-flag-uuid").val($(e.target).data("flag-uuid"));
                    $("#answer-team-uuid").val($(e.target).data("team-uuid"));
                    $("#answer-token").val(token);
                    $("#answer-flag").text(token);
                    if (penalty === "0") {
                        $("#pointrestore").hide();
                    } else {
                        $("#answer-penalty").text(penalty);
                    }
                    if (flagtype !== "static" && flagtype !== "regex") {
                        $("#acceptanswer").prop("checked", false);
                        $("#acceptanswer").prop("disabled", true);
                        $("#flagtypenote").show();
                    }
                    return false; 
                }
            );
        });
    }, 'json');
}

function resetAnswerModal() {
    $("#flagtypenote").hide();
    $("#pointrestore").show();
    $("#acceptanswer").prop("checked", true);
    $("#acceptanswer").prop("disabled", false);
    $("#details-flag-modal").modal('hide');
    $("#details-answer-modal").modal('show');
}

/* Add click events */
$(document).ready(function() {
    /* Flag Details */
    $("a[id^=details-flag-button]").click(function() {
        getStatDetails("flag", $(this).data("uuid"));
    });
    $('#details-answer-modal').on('hidden.bs.modal', function () {
        $("#details-flag-modal").modal('show');
    })
    $("#stat-answer-submit").click(function() {
        $("#stat-answer-form").submit();
    });
});