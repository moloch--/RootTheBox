function text_animation(term) {
    var index = 0;
    var flag = $('#flag').val();
    var reward = $('#reward').val();
    var msg = $('#capture-message').val();
    var banking = $('#banking').val();
    var intro_frames = [];
    if (flag.length > 0) {
        intro_frames.push("I have received the '" + flag + "' information.");
        intro_frames.push("  ");
        if (reward.length > 0) {
            if (banking === "$") {
                intro_frames.push("This is acceptable and I have transferred $" + reward + " to your\naccount.", " ");
            } else {
                intro_frames.push("This is acceptable and I have added " + reward + " points to your\nscore.", " ");
            }
        }
    }
    if (msg.toString() !== "" && msg.toString() !== "None") {
        msgsplit = msg.toString().split("\n\n")
        for (x in msgsplit) {
            intro_frames.push(msgsplit[x], " ");
        }
    }
    term.echo("[[b;;]**************** BEGIN SECURE COMMUNIQUE ****************]\n");

    function display(term, index) {
        term.echo(intro_frames[index]);
        index += 1;
        if (index < intro_frames.length) {
            setTimeout(display, 2000, term, index);
        } else {
            term.echo("[[b;;]**************** END OF TRANSMISSION ****************]");
        }
    }
    setTimeout(display, 1500, term, index);
}

function loading(term) {
    term.clear();
    var count = 0;
    loading_bar = ["|", "/", "-", "\\"];
    message = "\n[[b;;]> Establishing communication channel, please wait...]";

    function display(term, count) {
        term.clear();
        sym = loading_bar[count % loading_bar.length];
        term.echo(message + sym);
        count += 1;
        if (count < 35) {
            setTimeout(display, 100, term, count);
        } else {
            $(".c-glitch").empty();
            term.clear();
            text_animation(term);
        }
    }
    display(term, count);
}

function greetings(term) {
    term.pause();
    loading(term);
}

$(document).ready(function() {
    $("#closebutton").click(function(){
        if ($(this).val().length > 0) {
            window.location = '/user/missions/boxes?uuid=' + htmlEncode($(this).val());
        } else {
            window.location = '/user/missions';
        }
        
    });
    $('#console').terminal({
        /* No commands just animation */
    }, {
        prompt: " > ",
        name: 'console',
        greetings: null,
        tabcompletion: true,
        onInit: function(term) {
            greetings(term);
        },
    });
});