function text_animation(term) {
    var index = 0;
    var flag = $('#flag').val();
    var reward = $('#reward').val();
    var msg = $('#capture-message').val();
    var banking = $('#banking').val();
    intro_frames = [
        "  I have received the '" + flag + "' information.",
        "  ",
        "  " + msg.toString(),
        "  ",
        "  I have transfered " + banking + reward + " to your team's account.",
        " ",
        " Good hunting,\n    -Morris",
    ];
    term.echo("[[b;;]*************** BEGIN SECURE COMMUNIQUE ****************]\n");

    function display(term, index) {
        term.echo(intro_frames[index]);
        index += 1;
        if (index < intro_frames.length) {
            setTimeout(display, 2000, term, index);
        } else {
            term.echo("\n[[b;;]**************** END OF TRANSMISSION ****************]");
        }
    }
    setTimeout(display, 1500, term, index);
}

function loading(term) {
    term.clear();
    var count = 0;
    loading_bar = ["|", "/", "-", "\\"];
    message = " > Establishing secure communication channel, please wait... ";

    function display(term, count) {
        term.clear();
        sym = loading_bar[count % loading_bar.length];
        term.echo(message + sym);
        count += 1;
        if (count < 60) {
            setTimeout(display, 100, term, count);
        } else {
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