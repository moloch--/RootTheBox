function text_animation(term) {
    var index = 0;
    var flag = $('#flag').val();
    var reward = $('#reward').val();
    var msg = $('#capture-message').val();
    var banking = $('#banking').val();
    var intro_frames = [
        "I have received the '" + flag + "' information.",
        "  "
    ];
    if (banking === "$") {
        intro_frames.push("This is acceptable and I have transfered $" + reward + " to your\naccount.", " ");
    } else {
        intro_frames.push("This is acceptable and I have added " + reward + " points to your\nscore.", " ");
    }
    if (msg.toString() !== "" && msg.toString() !== "None") {
        intro_frames.push(msg.toString(), " ");
    }
    
    intro_frames.push("Good hunting,\n    -Morris", " ");

    term.echo("[[b;;]**************** BEGIN SECURE COMMUNIQUE ****************]\n");

    function display(term, index) {
        term.echo(intro_frames[index]);
        index += 1;
        if (index < intro_frames.length) {
            setTimeout(display, 1500, term, index);
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
        window.location = '/user/missions/boxes?uuid=' + $(this).val();
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