function text_animation(term) {
    var index = 0;
    var user = $('#handle').val();
    var reward = $('#reward').val();
    intro_frames = [
        " Hello [[b;;]" + user + "],\n",
        "   I am your new employer, you may call me [[b;;]Morris].",
        " ",
        "  I hope you're well rested.  We have a lot of work to do.",
        "  I have several assignments which require your... special skill set.",
        " ",
        "  You may view your current assignments by selecting \"Missions\" from the Game menu.",
        "  I will also be glad to rent your botnet for $" + reward + " per bot.",
        " ",
        "  I've taken the liberty of despositing some seed in your team's bank account,",
        "  see that it's put to good use.",
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