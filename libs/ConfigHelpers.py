
import logging

from tornado.options import options
from datetime import datetime


def save_config():
    logging.info("Saving current config to: %s" % options.config)
    with open(options.config, 'w') as fp:
        fp.write("##########################")
        fp.write(" Root the Box Config File ")
        fp.write("##########################\n")
        fp.write("# Last updated: %s\n" % datetime.now())
        for group in options.groups():
            # Shitty work around for Tornado 4.1
            if 'rootthebox.py' in group.lower() or group == '':
                continue
            fp.write("\n# [ %s ]\n" % group.title())
            for key, value in options.group_dict(group).iteritems():
                if isinstance(value, basestring):
                    # Str/Unicode needs to have quotes
                    fp.write(u'%s = "%s"\n' % (key, value))
                else:
                    # Int/Bool/List use __str__
                    fp.write('%s = %s\n' % (key, value))
