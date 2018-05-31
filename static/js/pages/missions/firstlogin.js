function text_animation(term) {
    var index = 0;
    var user = $('#handle').val();
    var reward = $('#reward').val();
    var bots = $('#usebots').val();
    var bank = $('#banking').val();
    intro_frames = [
        " Hello [[b;;]" + user + "],\n",
        "  I am your new employer. You may call me [[b;;]Morris].",
        " ",
        "  I hope you're well rested.  We have a lot of work to do.",
        "  I have several assignments which require your... special skill set.",
        " ",
        "  You may view your current assignments by selecting \"Missions\" from the Game menu.",
    ];
    if (bots === 'true') {
        intro_frames.push("  I will also be glad to rent your botnet for $" + reward + " per bot.");
    }
    if (bank === 'true') {
        intro_frames.push(" ",
            "  I've taken the liberty of depositing some seed money in your team's bank account.",
            "  See that it's put to good use."
        );
    }
    intro_frames.push(" ", " Good hunting,\n    -Morris");

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
