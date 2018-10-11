(function(document, history, location) {
    var HISTORY_SUPPORT = !!(history && history.pushState);
  
    var anchorScrolls = {
      ANCHOR_REGEX: /^#[^ ]+$/,
      OFFSET_HEIGHT_PX: 60,
  
      /**
       * Establish events, and fix initial scroll position if a hash is provided.
       */
      init: function() {
        this.scrollToCurrent();
        $(window).on('load', $.proxy(this, 'scrollToCurrent'));
        $(window).on('hashchange', $.proxy(this, 'scrollToCurrent'));
        $('body').on('click', 'a', $.proxy(this, 'delegateAnchors'));
      },
  
      /**
       * Return the offset amount to deduct from the normal scroll position.
       * Modify as appropriate to allow for dynamic calculations
       */
      getFixedOffset: function() {
        return this.OFFSET_HEIGHT_PX;
      },
  
      /**
       * If the provided href is an anchor which resolves to an element on the
       * page, scroll to it.
       * @param  {String} href
       * @return {Boolean} - Was the href an anchor.
       */
      scrollIfAnchor: function(href, pushToHistory) {
        var match, anchorOffset;
  
        if(!this.ANCHOR_REGEX.test(href)) {
          return false;
        }
  
        match = document.getElementById(href.slice(1));
  
        if(match) {
          anchorOffset = $(match).offset().top - this.getFixedOffset();
          $('html, body').animate({ scrollTop: anchorOffset});
  
          // Add the state to history as-per normal anchor links
          if(HISTORY_SUPPORT && pushToHistory) {
            history.pushState({}, document.title, location.pathname + href);
          }
        }
  
        return !!match;
      },
      
      /**
       * Attempt to scroll to the current location's hash.
       */
      scrollToCurrent: function(e) { 
        if(this.scrollIfAnchor(window.location.hash) && e) {
            e.preventDefault();
        }
      },
  
      /**
       * If the click event's target was an anchor, fix the scroll position.
       */
      delegateAnchors: function(e) {
        var elem = e.target;
  
        if(this.scrollIfAnchor(elem.getAttribute('href'), true)) {
          e.preventDefault();
        }
      }
    };
  
      $(document).ready($.proxy(anchorScrolls, 'init'));
      $(document).ready($.proxy(window, 'delegateAnchors'));
  })(window.document, window.history, window.location);
  
  
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