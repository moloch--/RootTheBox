var dialog;
function text_animation(term) {
    var index = 0;
    var intro_frames = $.parseJSON(dialog);

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
    setTimeout(display, 2000, term, index);
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
        window.location = '/user';
    });
    /* Update Summary Table */
    $.get("/user/missions/ajax/firstlogin", function(firstlogin) {
        dialog = firstlogin;
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
});
