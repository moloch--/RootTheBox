function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

function getAccess(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);
    data = {'uuid': uuid, 'obj': obj, '_xsrf': getCookie("_xsrf")}
    $.post('/admin/ajax/objects', data, function(response) {
        $('#availableList').empty();
        $('#accessList').empty();
        $.each(sortResults(response["available"], 'name', true), function (i, item) {
            $('#availableList').append($('<option>', { 
                value: item.uuid,
                text : item.name 
            }));
        });
        $.each(sortResults(response["access"], 'name', true), function (i, item) {
            $('#accessList').append($('<option>', { 
                value: item.uuid,
                text : item.name 
            }));
        });
        $.each(response, function(key, value) {  
           if (key === "type") {
                $("#" + obj + "-" + key + ' option[value=' + value + ']').prop('selected',true);
            } else {
                $("#" + obj + "-" + key).val(value);
            }
        });
    }, 'json');
}

function sortResults(item, prop, asc) {
    item.sort(function(a, b) {
        if (asc) {
            return (a[prop] > b[prop]) ? 1 : ((a[prop] < b[prop]) ? -1 : 0);
        } else {
            return (b[prop] > a[prop]) ? 1 : ((b[prop] < a[prop]) ? -1 : 0);
        }
    });
    return item;
}

function getDetails(obj, uuid) {
    $("#edit-" + obj + "-uuid").val(uuid);
    data = {'uuid': uuid, 'obj': obj, '_xsrf': getCookie("_xsrf")}
    $.post('/admin/ajax/objects', data, function(response) {
        $("#buyoutcost").show();
        if (response["number"] === 0) {
            $("#game_level-type option[value=progress]").prop('disabled',true);
            if (response["type"] === undefined || response["type"] === "progress" || (response["type"] === 'buyout' && response["buyout"] === 0)) {
                response["type"] = "none";
                $("#game_level-type option[value=none]").prop('selected', true);
                $("#game_level-buyout").val(0);
            }
        } else {
            $("#game_level-type option[value=progress]").prop('disabled',false);
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
    $('#addToLevel').click(function () {
        if ($('#availableList option:selected').val() != null) {
            var tempSelect = $('#availableList option:selected').val();
            $('#availableList option:selected').remove().appendTo('#accessList');
            $("#availableList").attr('selectedIndex', '-1').find("option:selected").removeAttr("selected");
            $("#accessList").attr('selectedIndex', '-1').find("option:selected").removeAttr("selected");
            $("#accessList").val(tempSelect);
            tempSelect = '';
        } else {
            alert("Before add please select any position.");
        }
    });
    
    $('#removeFromLevel').click(function () {
        if ($('#accessList option:selected').val() != null) {
            var tempSelect = $('#accessList option:selected').val();
            $('#accessList option:selected').remove().appendTo('#availableList');
            $("#accessList").attr('selectedIndex', '-1').find("option:selected").removeAttr("selected");
            $("#availableList").attr('selectedIndex', '-1').find("option:selected").removeAttr("selected");
          
            $("#availableList").val(tempSelect);
            tempSelect = '';
        } else {
            alert("Before remove please select any position.");
        }
    });

    /* Game Level */
    $("a[id^=edit-game-level-button]").click(function() {
        getDetails("game_level", $(this).data("uuid"));
    });

    $("#edit-game-level-submit").click(function() {
        $("#edit-game-level-form").submit();
    });

    $("button[id^=edit-access-button]").click(function() {
        getAccess("access", $(this).data("uuid"));
    });

    $("#edit-access-submit").click(function() {
        $('#accessList option').prop('selected', true);
        $('#availableList option').prop('selected', true);
        $("#edit-access-form").submit();
    });

    $("a[id^=delete-game-level-button]").click(function() {
         $("#delete-game-level-uuid").val($(this).data("uuid"));
    });

    $("#delete-game-level-submit").click(function() {
         $("#delete-game-level-form").submit();
    });

    $("a[id^=lock-level-button]").click(function() {
        $("#lock-level-uuid").val($(this).data("uuid"));
        $("#lock-level-form").submit();
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
        if (this.value === "none" || this.value === "hidden") {
            $("#buyoutcost").hide();
         } else if (this.value === "buyout") {
            $("#buyoutlabel").text("Unlock Cost");
            $("#game_level-buyout").attr('max', '');
            $("#buyout").attr('data-original-title', 'Unlock Cost');
            $("#buyout").attr('data-content', 'Cost to open this level and see flags [0-9]+');
            $("#buyoutcost").show();
         } else if (this.value === "progress") {
            $("#buyoutlabel").text("% Complete of Level " + $("#game_level-last_level").val());  
            $("#game_level-buyout").attr('max', 100);
            $("#buyout").attr('data-original-title', '% Complete of Prior Level');
            $("#buyout").attr('data-content', 'This level will unlock automatically after this percentage of prior level is completed (value 0-100).');
            $("#buyoutcost").show();
         } else if (this.value === "points") {
            $("#buyoutlabel").text("Score Points Earned");
            $("#game_level-buyout").attr('max', '');
            $("#buyout").attr('data-original-title', 'Score Points Earned');
            $("#buyout").attr('data-content', 'This level will unlock automatically after the score reaches this amount.');
            $("#buyoutcost").show();
         }
    });
});