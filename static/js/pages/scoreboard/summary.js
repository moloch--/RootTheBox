var glowtime = 30000;  //time score glows in ms
var fadetext = 20000;  //interval between hints taken / time since last capture fade effects
var scoretext = true;
var ranking = "";
var game_data = [];
var tableOptions = {
    onComplete: function(){ /*do nothing*/ },
    duration: [1000, 0, 700, 0, 500], //The milliseconds to do each phase and the delay between them
    extractIdFromCell: function(td){ return $.trim($(td).text()); }, //the function to use to extract the id value from a cell in the id column.
    animationSettings: {
        up: {
            left: -25, // Move left
            backgroundColor: '#004400' // Dullish green
        },
        down: {
            left: 25, // Move right
            backgroundColor: '#550000' // Dullish red
        },
        fresh: {
            left: 0, //Stay put in first stage.
            backgroundColor: 'transparent' // Yellow
        },
        drop: {
            left: 0, //Stay put in first stage.
            backgroundColor: 'transparent' // Purple
        }
    }
};

/* Update code */
$(document).ready(function() {
    if ($("#timercount_hidescoreboard").length > 0) {
        $.get("/scoreboard/ajax/timer", function(distance) {
            distance = distance * 1000;
            setTimer(distance, "_hidescoreboard");
        });
        window.scoreboard_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/pause_score");
        scoreboard_ws.onmessage = function(event) {
            if (event.data !== "pause") {
                location.reload();
            }
        }
    } else {
        if ($("#timercount").length > 0) {
            $.get("/scoreboard/ajax/timer", function(distance) {
                distance = distance * 1000;
                setTimer(distance, "");
            });
        }
        window.scoreboard_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/game_data");
        scoreboard_ws.onmessage = function(event) {
            if (event.data === "pause") {
                location.reload();
            } else {
                game_data = jQuery.parseJSON(event.data);
                
                /* Update Summary Table */
                let count = $("#parameters").data("count");
                let page = $("#parameters").data("page");
                $.get("/scoreboard/ajax/summary?count=" + count + "&page=" + page, function(table_data) {
                    highlight_table = highlights(table_data);
                    $("#summary_loading").hide();
                    if ($("#summary_tbody").find('tr').length == 0) {
                        $("#summary_tbody").html(highlight_table);
                        ranking = getRanking(table_data);
                    } else {
                        new_ranking = getRanking(table_data);
                        if (new_ranking === ranking) {
                            $("#summary_tbody").html(highlight_table);
                        } else {
                            //Animated Table Reorder
                            ranking = new_ranking;
                            var table = $("#summary_table").clone();
                            table.children('tbody').html(highlight_table);
                            $("#summary_table").rankingTableUpdate(table, tableOptions);
                        }
                    }
                    $("a[id^=team-details-button]").click(function() {
                        window.location = "/teams#" + $(this).data("uuid");
                    });
                    $("a[id^=user-details-button]").click(function() {
                        window.location = "/user?id=" + $(this).data("uuid");
                    }); 
                });
                if ($("#mvp_table").length > 0) {
                    /* Update MVP Table */
                    $.get("/scoreboard/ajax/mvp", function(table_data) {
                        $("#mvp_table").html(table_data);
                    });
                }
            }
        };
        setTimeout(changeDisplay, fadetext);
        setTimeout(updateLastFlag, 1000);
    }
    $("#page_count").on('change', function() {
        document.location.href = "/scoreboard?count=" + this.value + "&page=1";
    });
});

function changeDisplay() {
    if (scoretext) {
        if ($(".lastflagcol").text().length > 0) {
            $(".hintcol").fadeOut("slow", function() {
                $(".lastflagcol").fadeIn("slow");
            });
        }
        if ($("#mvp_table").length > 0) {
            $("#scoreboard_right_image").fadeOut("slow", function() {
                $("#scoreboard_mvp").fadeIn("slow");
            });
        }
    } else {
        if ($(".lastflagcol").text().length > 0) {
            $(".lastflagcol").fadeOut("slow", function() {
                $(".hintcol").fadeIn("slow");
            });
        }
        if ($("#scoreboard_right_image").length > 0) {
            $("#scoreboard_mvp").fadeOut("slow", function() {
                $("#scoreboard_right_image").fadeIn("slow");
            });
        }
    }
    scoretext = !scoretext;
    setTimeout(function () {     
        changeDisplay();
    }, fadetext);
}

function getRanking(table_data) {
    var new_rank = "";
    $(table_data).siblings("tr").each(function() {
        new_rank += $(this).attr("id");
    });
    return new_rank;
}

function highlights(table_data) {
    var table_data = $(table_data);
    //Set color of minibar
    $(table_data).find(".minibar").each(function() {
        if (this.style.width == "100%") {
            $(this).css('background-color', "#00bb00");
            $(this).css('background-image', 'linear-gradient(to bottom,#00bb00,#009900)')
        } else {
            $(this).css('background-color', "#eeee00");
            $(this).css('background-image', 'linear-gradient(to bottom,#eeee00,#b3b300)');
        }
    });
    if (!scoretext) {
        $(table_data).find(".hintcol").hide();
        $(table_data).find(".lastflagcol").show();
    } else {
        $(table_data).find(".lastflagcol").hide();
        $(table_data).find(".hintcol").show();
    }
    //Glow for new updates
    for (team in game_data) {
        if ("highlights" in game_data[team]) {
            var highlights = game_data[team]["highlights"];
            var now = highlights["now"];
            for (item in highlights) {
                if (item !== "now") {
                    var diff = now - highlights[item];
                    if (diff < glowtime) {
                        var column = $(table_data).siblings("#" + game_data[team]["uuid"]).find("." + item + "col");
                        if (!$(column).hasClass("glow")) {
                            var currentColumn = $("#summary_table").find("#" + game_data[team]["uuid"]).find("." + item + "col");
                            $(column).addClass("glow");
                            $(currentColumn).addClass("glow");
                            $(currentColumn).text($(column).text());
                            var id = setTimeout(function() {
                                $(column).removeClass("glow");
                            }, glowtime);
                            $(column).data("id", id);
                            $(currentColumn).data("id", id);
                        } else {
                            //already glowing - set new timeout
                            clearTimeout($(column).data("id"));
                            var id = setTimeout(function() {
                                $(column).removeClass("glow");
                            }, glowtime);
                            $(column).data("id", id);
                        }
                    }
                }
            }
        }
    }
    return table_data;
}

function updateLastFlag() {
    for (team in game_data) {
        if ("highlights" in game_data[team]) {
            var highlights = game_data[team]["highlights"];
            var money = highlights["money"];
            if (money !== 0) {
                var now = highlights["now"];
                var diff = now - money;
                $("#last-" + game_data[team]["uuid"]).text(timeConversion(diff) + " " + $("#summary_table").data("since-score"));
                highlights["now"] = now + 1000;
            }
        }
    }
    setTimeout(updateLastFlag, 1000);
}

function padDigits(number, digits) {
    return Array(Math.max(digits - String(number).length + 1, 0)).join(0) + number;
}
  
function setTimer(distance, id) {
    // Update the count down every 1 second
    var x = setInterval(function() {
        // Time calculations for days, hours, minutes and seconds
        var days = Math.max(0,Math.floor((distance) / (1000 * 60 * 60 * 24)));
        var hours = Math.max(0,Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)));
        var minutes = Math.max(0,Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)));
        var seconds = Math.max(0,Math.floor((distance % (1000 * 60)) / 1000));

        // Display the result in the element with id="timercount"
        var timercount = padDigits(minutes,2) + "m " + padDigits(seconds,2) + "s ";
        if (hours > 0) {
            timercount = hours + "h " + timercount;
        }
        if (days > 0) {
            timercount = days + "d " + timercount;
        }
        $("#timercount" + id).text(timercount);

        // If the count down is finished, write some text
        if (distance <= 0) {
            clearInterval(x);
            $("#timercount" + id).text("EXPIRED");
        }
        distance = distance - 1000;
    }, 1000);
}

function timeConversion(s) {
   
    // Pad to 2 or 3 digits, default is 2
    function pad(prior, n, z) {
        if (prior > 0) {
            z = z || 2;
            return ('00' + n).slice(-z);
        } else {
            return n;
        }
    }

    var s = parseInt(s / 1000);
    var secs = s % 60;
    s = (s - secs) / 60;
    var mins = s % 60;
    var hrs = (s - mins) / 60;
    var flagtime = "";
    if (hrs > 0) {
        flagtime += hrs + ':';
    }
    if (flagtime.length > 0 || mins > 0) {
        flagtime += pad(hrs, mins) + ":"
    }
    if (flagtime.length > 0 || secs > 0) {
        flagtime += pad(hrs + mins, secs);
    }
    if (flagtime.length === 0) {
        return 0;
    }
    return flagtime;
}