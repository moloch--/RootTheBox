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

    //Find all the strings
    doc = $(document);
    for (item in doc) {
        var text = $(item).text().trim().split();
        for (item in text) {
            if (text[item].length > 0) {
                var str = text[item].trim().split("\n");
                for (x in str) {
                    if (str[x].trim().length > 0) {
                        console.log(str[x].trim());
                    }
                    
                }
            }
            
        }
        
    }
    var sd = doc.find(':input');
    for (s in sd) {
        if (typeof sd[s] !== "function") {
            var placeholder = $(sd[s]).attr("placeholder");
            if (placeholder != null && placeholder.trim().length > 0) {
                console.log(placeholder.trim());
            }
        }
    }
});
