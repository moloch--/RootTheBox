$(document).ready(function() {
  window.scoreboard_ws = new WebSocket(wsUrl() + "/scoreboard/wsocket/pause_score");
        
  if ($("#timercount").length > 0) {
      $.get("/scoreboard/ajax/timer", function(distance) {
          distance = distance * 1000;
          setTimer(distance);
      });
      scoreboard_ws.onmessage = function(event) {
          if (event.data !== "pause") {
              location.reload();
          }
      }
  } else {
      scoreboard_ws.onmessage = function(event) {
          if (event.data === "pause") {
              location.reload();
          }
      }
  }
});

function padDigits(number, digits) {
  return Array(Math.max(digits - String(number).length + 1, 0)).join(0) + number;
}

function setTimer(distance) {
  // Update the count down every 1 second
  var x = setInterval(function () {
    // Time calculations for days, hours, minutes and seconds
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Display the result in the element with id="demo"
    var hourval = "";
    if (hours > 0) {
      hourval = hours + "h ";
    }
    $("#timercount").text(hourval + padDigits(minutes, 2) + "m " + padDigits(seconds, 2) + "s ");

    // If the count down is finished, write some text
    if (distance < 0) {
      clearInterval(x);
      $("#timercount").text("EXPIRED");
    }
    distance = distance - 1000;
  }, 1000);
}