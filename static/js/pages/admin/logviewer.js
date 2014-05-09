


function escapeHtml(value) {
    return $('<div/>').text(value).html();
}

$(document).ready(function() {
    var log_ws = new WebSocket($("#ws-connect").data("url")+"/admin/logviewer/wsocket");
    log_ws.onmessage = function(evt) {
        var emit = jQuery.parseJSON(evt.data);
        for (var index = 0; index < emit['messages'].length; index++) {
            line = emit['messages'][index].toString();
            $('#log-view').prepend(escapeHtml(line) + "\n");
        }
    };
});