
/* Update code */
$(document).ready(function() {
    
    if ($("#timercount").length > 0) {
        $.get("/scoreboard/ajax/timer", function(distance) {
            distance = distance * 1000;
            setTimer(distance);
        });
        window.scoreboard_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/pause_score");
        scoreboard_ws.onmessage = function(event) {
            if (event.data !== "pause") {
                location.reload();
            }
        }
    } else {
        window.scoreboard_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/game_data");
        scoreboard_ws.onmessage = function(event) {
            if (event.data === "pause") {
                location.reload();
            } else {
                game_data = jQuery.parseJSON(event.data);
                console.log(game_data);
                
                /* Update Summary Table */
                $.get("/scoreboard/ajax/summary", function(table) {
                    $("#summary_table").html(table);
                    $("a[id^=team-details-button]").click(function() {
                        window.location = "/teams#" + $(this).data("uuid");
                    });
                    barcolor();
                });
                if ($("#mvp_table").length > 0) {
                    /* Update MVP Table */
                    $.get("/scoreboard/ajax/mvp", function(table) {
                        $("#mvp_table").html(table);
                    });
                }
            }
        };
    }
});


function padDigits(number, digits) {
    return Array(Math.max(digits - String(number).length + 1, 0)).join(0) + number;
}
  
function setTimer(distance) {
    // Update the count down every 1 second
    var x = setInterval(function() {
        // Time calculations for days, hours, minutes and seconds
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        // Display the result in the element with id="demo"
        var hourval = "";
        if (hours > 0) {
        hourval = hours + "h ";
        }
        $("#timercount").text(hourval + padDigits(minutes,2) + "m " + padDigits(seconds,2) + "s ");

        // If the count down is finished, write some text
        if (distance < 0) {
        clearInterval(x);
        $("#timercount").text("EXPIRED");
        }
        distance = distance - 1000;
    }, 1000);
}