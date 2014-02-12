var logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR'];

function escapeHtml(value) {
    return $('<div/>').text(value).html();
}

function getLevel(msg) {
    return msg.substring(msg.indexOf('[') + 1, msg.indexOf(']'));
}

$(document).ready(function() {
    var minLevel = logLevels.indexOf($('#log-level').value);
    var log_ws = new WebSocket($("#ws-connect").val()+"/admin/logviewer/wsocket");
    log_ws.onmessage = function(evt) {
        var emit = jQuery.parseJSON(evt.data);
        for (var index = 0; index < emit['messages'].length; index++) {
            line = emit['messages'][index].toString();
            level = getLevel(line);
            if (minLevel <= logLevels.indexOf(level)) {
                $('#log-view').prepend(escapeHtml(line) + "\n");
            }
        }
    };
});