var logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR'];
    var entityMap = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': '&quot;',
        "'": '&#39;',
        "/": '&#x2F;'
    };

    function escapeHtml(string) {
        return String(string).replace(/[&<>"'\/]/g, function(s) {
            return entityMap[s];
        });
    }

    function getLevel(msg) {
        return msg.substring(msg.indexOf('[') + 1, msg.indexOf(']'));
    }
    var notifier_ws;
    $(document).ready(function() {
        var minLevel = logLevels.indexOf(document.getElementById('log-level').value);
        notifier_ws = new WebSocket($("#ws-connect").val()+"/admin/logviewer/wsocket");
        notifier_ws.onmessage = function(evt) {
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