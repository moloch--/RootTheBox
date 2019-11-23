$(document).ready(function() {
    $.get("/scoreboard/ajax/feed", function(feed) {
        $("#snippet").find("pre").text(JSON.stringify(feed, undefined, 4));
    });
});