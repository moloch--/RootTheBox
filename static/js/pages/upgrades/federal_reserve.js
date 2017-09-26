var password;

if (localStorage["cwd"] == undefined) {
    localStorage["cwd"] = "~";
}

function get_longest(line, diplay_buffer) {
    tmp = [];
    for (var index = 0; index < display_buffer.length; index++) {
        tmp.push(display_buffer[index][line]);
    }
    longest = tmp.reduce(function (a, b) {
         return a.toString().length > b.toString().length ? a : b;
    });
    return longest.toString().length;
}

function get_prompt() {
    if (localStorage["intro"] == undefined || localStorage["intro"] != "metasploit") {
        return 'root@mainframe:' + localStorage["cwd"] + '# ';
    } else {
        return '[[u;;]meterpreter] > ';
    }
}

function str_multi(str, num) {
    if (num < 0) num =  0;
    return num ? Array(num + 1).join(str) : "";
}

function print_info(term, message) {
    term.echo("[[;#0066FF;#000]-*-] " + message.toString());
}

function print_error(term, message) {
    term.echo("[[;#FF0000;#000]-!-] " + message.toString());
}

function print_data(term, display_buffer) {
    col_widths = [];
    for (var index = 0; index < display_buffer[0].length; index++) {
        col_widths[index] = get_longest(index, display_buffer);
    }
    div_str = "+"
    for (var index = 0; index < col_widths.length; index++) {
        div_str += "-" + str_multi("-", col_widths[index]) + "-";
        div_str += "+";
    }
    for (var index = 0; index < display_buffer.length; index++) {
        term.echo(div_str);
        buf = "|";
        for (var inner_index = 0; inner_index < display_buffer[index].length; inner_index++) {
            info = display_buffer[index][inner_index].toString();
            padding = col_widths[inner_index] - info.length;
            buf = buf + " " + info + str_multi(" ", padding) + " ";
            buf += "|";
        }
        term.echo(buf);
    }
    term.echo(div_str);
}

function attempt_xfer(term, password) {
    var src_account = localStorage['src_account'];
    var dest_account = localStorage['dest_account'];
    var amount = localStorage['amount'];
    var user = localStorage['user'];
    if (src_account == undefined) {
        print_error(term, "Source account is not defined");
    } else if (dest_account == undefined) {
        print_error(term, "Destination account is not defined");
    } else if (user == undefined) {
        print_error(term, "Authorized user is not defined");
    } else if (amount == undefined) {
        print_error(term, "Amount is not defined");
    } else {
        term.pause();
        term.echo(" ");
        print_info(term, "Attempting to transfer $" + amount.toString() + " '" + src_account + "' -> '" + dest_account + "'");
        args = {
            '_xsrf': document.getElementsByName("_xsrf")[0].value,
            'source': src_account,
            'destination': dest_account,
            'user': user,
            'amount': amount,
            'password': password,
        }
        $.post('/federal_reserve/json/xfer', args, function(results) {
            term.echo(" ");
            if (results == null) {
                print_error(term, "ERROR: Malformed response from server");
            } else {
                if ('success' in results) {
                    term.echo("[[b;#00FF00;]-$-] " + results['success']);
                } else if ('error' in results) {
                    print_error(term, "ERROR: " + results['error']);
                } else {
                    print_error(term, "ERROR: Unknown response from server");
                }
            }
            term.echo(" ");
            term.resume();
        });
    }
}
function greetings(term) {
    term.pause();
    var index = 0;
    var msframes = [
        "Started bind handler",
        "Automatically detecting the target ...",
        "Fingerprint: Winblows XP - Service Pack 7 - lang:Unknown",
        "We could not detect the language pack, defaulting to English",
        "Selected Target: Winblows XP SP7 English (AlwaysOn NX)",
        "Attempting to trigger the vulnerability ...",
        "Sending stage (1337 bytes) to 192.268.57.131",
        "Meterpreter session 1 opened (21.32.257.133:443 -> 192.268.57.131:1045)"
    ];
    ascii_frames = [
        " > Hacking mainframe, please wait ...",
        " > Hooking function pointer at: 0xfeeb3d0c",
        " > Initializing sat com units ...",
        " > Breaking cryptographic ip tunnel backtrace, please wait ...",
        " > Loading the blackhat file(s) from irc shipping channel",
        " > Mainframe: [[;#00FF00;]Access Granted]",
    ];
    function display(term, index) {
        if (localStorage["intro"] == undefined) {
            localStorage["intro"] = "ascii"; // Default option
        }
        if (localStorage["intro"] == "metasploit") {
            print_info(term, msframes[index]);
            index++;
            if (index < msframes.length) {
                delay = Math.floor((Math.random() * 1000) + 400);
                setTimeout(display, delay, term, index);
            } else {
                term.echo(" ");
                term.resume();
            }
        } else if (localStorage["intro"] == "ascii") {
            if (index < ascii_frames.length) {
                term.echo(ascii_frames[index]);
                index++;
                delay = Math.floor((Math.random() * 800) + 400);
                setTimeout(display, delay, term, index);
            } else {
                term.echo(" ");
                term.echo("[[b;;]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FEDERAL RESERVE &nbsp;TRANSFER NODE]");
                term.echo(" ");
                term.echo("[[;;]&nbsp;&nbsp;&nbsp;&nbsp;********* Remote Systems Input Station *********]");
                term.echo("[[;;]&nbsp;&nbsp;&nbsp;&nbsp;================================================]");
                term.echo(" ");
                term.resume();
            }
        } else {
            print_info(term, "Startings console ...");
            term.resume();
        }
    }
    display(term, index);
}

$(document).ready(function() {
    $('#console').terminal({
            users: function() {
                term = this;
                term.echo(" ");
                print_info(term, "Querying database, please wait ...");
                term.pause();
                $.getJSON('/federal_reserve/json/ls?data=users', function(data) {
                    if ('users' in data) {
                        users = data['users'];
                        // console.log(users);
                        display_buffer = [];
                        display_buffer[0] = ["id", "Account", "Name", "Password"];
                        var count = 1;
                        $.each(users, function(key, val) {
                            display_buffer[count] = [];
                            display_buffer[count][0] = count;
                            display_buffer[count][1] = val["account"];
                            display_buffer[count][2] = key;
                            display_buffer[count][3] = val["password"];
                            count += 1;
                        });
                        term.echo(" ");
                        print_data(term, display_buffer);
                    } else {
                        print_error(term, "ERROR: Request failed.")
                    }
                    term.resume();
                });
            },
            accounts: function() {
                term = this;
                term.echo(" ");
                print_info(term, "Querying database, please wait ...");
                term.pause();
                $.getJSON('/federal_reserve/json/ls?data=accounts', function(data) {
                    if ('accounts' in data) {
                        accounts = data['accounts'];
                        // console.log(accounts);
                        display_buffer = [];
                        display_buffer[0] = ["id", "Account", "Balance", "Flags", "Bots"];
                        var count = 1;
                        $.each(accounts, function(key, val) {
                            display_buffer[count] = [];
                            display_buffer[count][0] = count;
                            display_buffer[count][1] = key;
                            display_buffer[count][2] = "$" + val["money"];
                            display_buffer[count][3] = val["flags"];
                            display_buffer[count][4] = val["bots"];
                            count += 1;
                        });
                        term.echo(" ");
                        print_data(term, display_buffer);
                    } else {
                        print_error(term, "ERROR: Request failed.")
                    }
                    term.resume();
                });
            },
            transfer: function() {
                term = this;
                term.echo(" ");
                term.echo("[[b;;]*** TRANSFER FUNDS ***]");
                term.echo(" ");
                term.push(function(user) {
                    localStorage.setItem("user", user);
                    term.pop();
                    term.set_mask(true);
                    term.push(function(passwd) {
                            attempt_xfer(term, passwd);
                            term.pop();
                            term.set_mask(false);
                        }, {
                            prompt: "\tPassword: ",
                        }
                    );
                }, {
                    prompt: "[[;#990066;#000]-?-] Authorized User: ",
                });
                term.push(function(amount) {
                    localStorage.setItem("amount", amount);
                    term.pop();
                }, {
                    prompt: "[[;#990066;#000]-?-] Transfer Amount: $",
                });
                term.push(function(src_account) {
                    localStorage.setItem("src_account", src_account);
                    term.pop();
                }, {
                    prompt: "[[;#990066;#000]-?-] Source Account Name (transfer from): ",
                });
                term.push(function(dest_account) {
                    localStorage.setItem("dest_account", dest_account);
                    term.pop();
                }, {
                    prompt: "[[;#990066;#000]-?-] Destination Account Name (transfer to): ",
                });
            },
            intro: function(value) {
                if (value != undefined) {
                    value = String(value).toLowerCase();
                }
                if (value == "off" || value == "ascii" || value == "metasploit") {
                    localStorage["intro"] = value;
                    this.echo(" ");
                    print_info(this, "[[b;;]Intro] set to '" + localStorage["intro"] + "'");
                    this.echo(" ");
                } else {
                    print_error(this, "ERROR: Not a valid option; 'off', 'ascii', or 'metasploit'");
                }
            },
            ifconfig: function() {
                this.echo("eth0\t      Link encap:Ethernet  HWaddr 00:13:37:ff:e4:90");
                this.echo("\t\tinet addr:192.168.293.345  Mask:255.0.0.0");
                this.echo("\t\tUP BROADCAST MULTICAST  MTU:1500  Metric:1");
                this.echo("\t\tRX packets:0 errors:0 dropped:0 overruns:0 frame:0");
                this.echo("\t\tTX packets:0 errors:0 dropped:0 overruns:0 carrier:0");
                this.echo("\t\tcollisions:0 txqueuelen:1000 ");
                this.echo("\t\tRX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)");
                this.echo("\t\tInterrupt:20 Memory:f2400000-f2420000 ");
                this.echo(" ");
                this.echo("lo&nbsp;&nbsp;\t        Link encap:Local Loopback ");
                this.echo("\t\tinet addr:127.0.0.1  Mask:255.0.0.0");
                this.echo("\t\tinet6 addr: ::1/128 Scope:Host");
                this.echo("\t\tUP LOOPBACK RUNNING  MTU:16436  Metric:1");
                this.echo("\t\tRX packets:97759 errors:0 dropped:0 overruns:0 frame:0");
                this.echo("\t\tTX packets:97759 errors:0 dropped:0 overruns:0 carrier:0");
                this.echo("\t\tcollisions:0 txqueuelen:0 ");
            },
            ls: function() {
                if (localStorage["cwd"] == "/" || localStorage["cwd"] == undefined) {
                    this.echo("drwxr-xr-x   2 root\t     root\t     4.0K Nov 27 12:33 bin/");
                    this.echo("drwxr-xr-x   4 root\t     root\t     1.0K Nov 30 04:10 boot/");
                    this.echo("drwxr-xr-x   2 root\t     root\t     4.0K Nov&nbsp;  8 15:08 cdrom/");
                    this.echo("drwxr-xr-x   5 root\t     root\t     4.4K Dec&nbsp;  3 21:08 dev/");
                    this.echo("drwxr-xr-x   7 root\t     root\t     112K Dec&nbsp;  3 21:08 etc/");
                    this.echo("drwxr-xr-x   3 root\t     root\t     4.0K Nov&nbsp;  8 15:09 home/");
                    this.echo("drwxr-xr-x   4 root\t     root\t     4.0K Nov 27 22:26 lib/");
                    this.echo("drwxr-xr-x   2 root\t     root\t     4.0K Oct 17 07:56 lib64/");
                    this.echo("drwx------   2 root\t     root\t     160K Nov&nbsp;  8 15:06 lost+found/");
                    this.echo("drwxr-xr-x   3 root\t     root\t     4.0K Nov&nbsp;  8 16:32 media/");
                    this.echo("drwxr-xr-x   2 root\t     root\t     4.0K Oct&nbsp; 9 08:03 mnt/");
                    this.echo("drwxr-xr-x   4 root\t     root\t     4.0K Nov&nbsp;  8 22:33 opt/");
                    this.echo("dr-xr-xr-x   6 root\t     root\t     0.0K Dec&nbsp;  3 21:07 proc/");
                    this.echo("drwx------   0 root\t     root\t     4.0K Nov 27 10:21 root/");
                    this.echo("drwxr-xr-x   9 root\t     root\t     1.1K Dec&nbsp;  3 21:08 run/");
                    this.echo("drwxr-xr-x   2 root\t     root\t     200K Nov 27 12:33 sbin/");
                    this.echo("drwxr-xr-x   2 root\t     root\t     4.0K Jun 11 11:36 selinux/");
                    this.echo("drwxr-xr-x   2 root\t     root\t     4.0K Oct 17 07:56 srv/");
                    this.echo("dr-xr-xr-x   3 root\t     root\t     0.0K Dec&nbsp;  3 21:07 sys/");
                    this.echo("drwxrwxrwt   2 root\t     root\t     4.0K Dec&nbsp;  3 23:38 tmp/");
                    this.echo("drwxr-xr-x   1 root\t     root\t     4.0K Nov&nbsp;  8 15:17 usr/");
                    this.echo("drwxr-xr-x   5 root\t     root\t     4.0K Nov&nbsp;  9 12:36 var/");
                } else if (localStorage["cwd"] == "/root") {
                    this.echo("drwxr-xr-x 22 root\t root\t 4.0K Nov  8 15:14 ./");
                    this.echo("drwxr-xr-x 54 root\t root\t 4.0K Dec  4 00:06 ../");
                    this.echo("drwxr-xr-x 54 root\t root\t 4.0K Dec  4 00:06 .ssh/");
                } else {
                    this.echo("drwxr-xr-x 22 root\t root\t 4.0K Nov  8 15:14 ./");
                    this.echo("drwxr-xr-x 54 root\t root\t 4.0K Dec  4 00:06 ../");
                }
                this.echo(" ");
            },
            cat: function(file) {
                if (file == undefined) {
                    this.echo(" ");
                } else if (file == "/etc/passwd") {
                    this.echo("root:x:0:0:root:/root:/bin/bash");
                    this.echo("daemon:x:1:1:daemon:/usr/sbin:/bin/sh");
                    this.echo("bin:x:2:2:bin:/bin:/bin/sh");
                    this.echo("sys:x:3:3:sys:/dev:/bin/sh");
                    this.echo("sync:x:4:65534:sync:/bin:/bin/sync");
                    this.echo("games:x:5:60:games:/usr/games:/bin/sh");
                    this.echo("man:x:6:12:man:/var/cache/man:/bin/sh");
                    this.echo("lp:x:7:7:lp:/var/spool/lpd:/bin/sh");
                    this.echo("mail:x:8:8:mail:/var/mail:/bin/sh");
                    this.echo(" ");
                }
            },
            whoami: function() {
                this.echo("root");
                this.echo(" ");
            },
            cd: function(dir) {
                localStorage["cwd"] = dir;
                this.set_prompt("root@mainframe:" + localStorage["cwd"] + "# ");
                this.echo(" ");
            },
            pwd: function() {
                if (localStorage["cwd"] == "~") {
                    this.echo("/root");
                } else {
                    this.echo(localStorage["cwd"]);
                }
                this.echo(" ");
            },
            help: function() {
                this.echo(" ");
                this.echo(" [[b;;]accounts] - Get a list of active bank accounts");
                this.echo(" [[b;;]users]    - Get information on users");
                this.echo(" [[b;;]transfer] - Transfer funds from one account to another");
                this.echo(" [[b;;]intro]    - Change console intro animation");
                this.echo(" ");
            }
        }, {
            prompt: get_prompt(),
            name: 'console',
            greetings: null,
            tabcompletion: true,
            onInit: function(term) {
                greetings(term);
            },
        }
    );
});