import logging, os

from tornado.options import options
from datetime import datetime
from past.builtins import basestring
from .ConsoleColors import *


def save_config():
    if os.path.isfile(options.config):
        resp = (
            str(
                input(
                    PROMPT
                    + "A configuration file already exists.  Do you want to overwrite this configuration [N/y]? "
                )
            )
            or "N"
        )
        if (
            resp.replace('"', "").lower().strip() != "y"
            and resp.replace('"', "").lower().strip() != "yes"
        ):
            return
    print(INFO + "Saving current config to: %s" % options.config)
    with open(options.config, "w") as fp:
        fp.write("##########################")
        fp.write(" Root the Box Config File ")
        fp.write("##########################\n")
        fp.write(
            "# Documentation: %s\n"
            % "https://github.com/moloch--/RootTheBox/wiki/Configuration-File-Details"
        )
        fp.write("# Last updated: %s\n" % datetime.now())
        for group in options.groups():
            # Shitty work around for Tornado 4.1
            if "rootthebox.py" in group.lower() or group == "":
                continue
            fp.write("\n# [ %s ]\n" % group.title())
            opt = list(options.group_dict(group).items())
            for key, value in opt:
                try:
                    # python2
                    value_type = basestring
                except NameError:
                    # python 3
                    value_type = str
                if isinstance(value, value_type):
                    # Str/Unicode needs to have quotes
                    fp.write('%s = "%s"\n' % (key, value))
                else:
                    # Int/Bool/List use __str__
                    fp.write("%s = %s\n" % (key, value))
    if options.save:
        print(
            INFO
            + bold
            + "If necessary, update the db username and password in the cfg and set any advanced configuration options."
        )
