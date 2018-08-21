function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function getDetails(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);
    data = {'uuid': uuid, 'obj': obj, '_xsrf': getCookie("_xsrf")}
    $.post('/admin/ajax/objects', data, function(response) {
        if (response["number"] === 0) {
            $("#gametype").hide();
            $("#buyoutcost").hide();
            response["type"] = "none"
            $("#game_level-type option[value=none]").prop('selected',true);
            $("#game_level-buyout").val(0);
        } else {
            $("#gametype").show();
            $("#buyoutcost").show();
        }
        if (response["type"] === "none") {
            $("#buyoutcost").hide();    
        } else if (response["type"] == "buyout") {
            if (response["buyout"] === 0) {
                response["type"] = "none"
                $("#buyoutcost").hide();
            } else {
                $("#buyoutlabel").text("Unlock Cost");
                $("#game_level-buyout").attr('max', '');
            }
        } else {
            $("#buyoutlabel").text("% Complete of Level " + response["last_level"]);
            $("#game_level-buyout").attr('max', 100);
        }

        $.each(response, function(key, value) {  
           if (key === "type") {
                $("#" + obj + "-" + key + ' option[value=' + value + ']').prop('selected',true);
            } else {
                $("#" + obj + "-" + key).val(value);
            }
        });
    }, 'json');
}

/* Add click events */
$(document).ready(function() {

    /* Game Level */
    $("a[id^=edit-game-level-button]").click(function() {
        getDetails("game_level", $(this).data("uuid"));
    });

    $("#edit-game-level-submit").click(function() {
        $("#edit-game-level-form").submit();
    });

    $("a[id^=delete-game-level-button]").click(function() {
         $("#delete-game-level-uuid").val($(this).data("uuid"));
    });

    $("#delete-game-level-submit").click(function() {
         $("#delete-game-level-form").submit();
    });

    /* Switch Level */
    $("a[id^=switch-level-button]").click(function() {
        $("#game-level-uuid").val($(this).data("level-uuid"));
        $("#box-uuid").val($(this).data("box-uuid"));
    });

    $("#switch-level-submit").click(function() {
        $("#switch-level-form").submit();
    });

    $("#game_level-type").change(function() {
         if (this.value === "none") {
            $("#buyoutcost").hide(); 
         } else if (this.value === "buyout") {
            $("#buyoutlabel").text("Unlock Cost");
            $("#game_level-buyout").attr('max', '');
            $("#buyoutcost").show();
         } else if (this.value === "progress") {
            $("#buyoutlabel").text("% Complete of Level " + $("#game_level-last_level").val());  
            $("#game_level-buyout").attr('max', 100);
            $("#buyoutcost").show();
         }
    });
});