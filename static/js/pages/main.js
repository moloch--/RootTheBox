function wsUrl() {
    if (window.location.protocol != "https:") {
        return "ws://" + window.location.host
    } else {
        return "wss://" + window.location.host
    }
}

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) {
        return parts.pop().split(";").shift();
    }
}

function htmlEncode(value) {
    return $('<div/>').text(value).html();
}

$(document).ready(function() {
    if ($("#logout").length) {
        $("#logout").click(function() {
            $("#logout-form").submit();
        });
    }
});
