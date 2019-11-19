import logging

from tornado.options import options
from datetime import datetime
from past.builtins import basestring


def save_config():
    logging.info("Saving current config to: %s" % options.config)
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
