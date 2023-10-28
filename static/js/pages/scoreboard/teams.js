$(document).ready(function() {
  window.scoreboard_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/pause_score");
        
  if ($("#timercount_hidescoreboard").length > 0) {
      $.get("/scoreboard/ajax/timer", function(distance) {
            distance = distance * 1000;
            setTimer(distance, "_hidescoreboard");
        });
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
      scoreboard_ws.onmessage = function(event) {
          if (event.data === "pause") {
              location.reload();
          }
      }
  }
  $("#page_count").on('change', function() {
    document.location.href = "/teams?count=" + this.value + "&page=1";
  });
});

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