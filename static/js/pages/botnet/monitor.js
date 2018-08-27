$(document).ready(function() {
    $('#table-footer').text('WebSocket Connecting ...');
    var monitor_ws = new WebSocket(wsUrl() + "/botnet/webmonitor");

    monitor_ws.onerror = function (evt) {
        alert("ERROR: " + evt.data.toString());
    };

    monitor_ws.onmessage = function (evt) {
        msg = jQuery.parseJSON(evt.data);
        if ('opcode' in msg) {
            if (msg['opcode'] == 'update' && 'bots' in msg) {
                bots = msg['bots'];
                $('#box-table').text('');
                $('#table-footer').text('');
                if (0 < bots.length) {
                    for (var index = 0; index < bots.length; index++) {
                        $('#box-table').append(
                            "<tr>" +
                                "<td> " + (index + 1).toString() + "</td>" +
                                "<td class='teamname'> " + escapeHtml(bots[index]['team_name']) + "</td>" +
                                "<td> " + escapeHtml(bots[index]['box_name']) + "</td>" +
                                "<td> " + escapeHtml(bots[index]['remote_ip']) + "</td>" +
                                "<td>$" + escapeHtml(bots[index]['total_reward']) + "</td>" +
                                "<td> " + escapeHtml(bots[index]['last_ping']) + "</td>" +
                            "<tr>"
                        );
                    }
                } else {
                    $('#table-footer').text('No bots yet, get hacking!');
                }
            } else {
                alert("Error: Update contains no bots.");
            }
        } else {
            alert("Error: Malformed message from server.");
        }
    };
});

var entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
    '/': '&#x2F;',
    '`': '&#x60;',
    '=': '&#x3D;'
  };

  function escapeHtml (string) {
    return String(string).replace(/[&<>"'`=\/]/g, function fromEntityMap (s) {
      return entityMap[s];
    });
  }