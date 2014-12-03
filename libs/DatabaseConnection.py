import os
import urllib
import logging

from libs.ConsoleColors import *
from sqlalchemy import create_engine
from tornado.options import options


class DatabaseConnection(object):

    def __init__(self, database, hostname='', port='',
                 username='', password='', dialect=''):
        self.database = database
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.dialect = dialect

    def __str__(self):
        ''' Construct the database connection string '''
        if self.dialect == 'sqlite':
            db_conn = self._sqlite()
        elif self.dialect.startswith('postgres'):
            db_conn = self._postgresql()
        elif self.dialect == 'mysql':
            db_conn = self._mysql()
        else:
            raise ValueError("Database dialect not supported")
        self._test_connection(db_conn)
        return db_conn

    def _postgresql(self):
        '''
        Configured to use postgresql, there is no built-in support
        for postgresql so make sure we can import the 3rd party
        python lib 'pypostgresql'
        '''
        logging.debug("Configured to use Postgresql for a database")
        try:
            import pypostgresql
        except ImportError:
            print(WARN + "You must install 'pypostgresql'")
            os._exit(1)
        db_host, db_name, db_user, db_password = self._db_credentials()
        return 'postgresql+pypostgresql://%s:%s@%s/%s' % (
            db_user, db_password, db_host, db_name,
        )

    def _sqlite(self):
        '''
        SQLite connection string, always save db file to cwd, or in-memory
        '''
        logging.debug("Configured to use SQLite for a database")
        db_name = os.path.basename(self.config.get("Database", 'name'))
        if 0 == len(db_name):
            db_name = 'rtb'
        return 'sqlite:///%s.db' % db_name

    def _mysql(self):
        ''' Configure db_connection for MySQL '''
        logging.debug("Configured to use MySQL for a database")
        db_server, db_name, db_user, db_password = self._db_credentials()
        return 'mysql://%s:%s@%s/%s' % (
            db_user, db_password, db_server, db_name
        )

    def _test_connection(self, connection_string):
        '''
        Test the connection string to see if we can connect to the database
        '''
        engine = create_engine(connection_string)
        try:
            connection = engine.connect()
            connection.close()
        except:
            if options.debug:
                logging.exception("Database connection failed")
            logging.critical("Failed to connect to database, check settings")
            os._exit(1)

    def _db_credentials(self):
        ''' Pull db creds and return them url encoded '''
        if self.password == '' or self.password == 'RUNTIME':
            sys.stdout.write(PROMPT + "Database password: ")
            sys.stdout.flush()
            self.password = getpass.getpass()
        db_host = urllib.quote(self.hostname)
        db_name = urllib.quote(self.database)
        db_user = urllib.quote(self.username)
        db_password = urllib.quote_plus(self.password)
        return db_host, db_name, db_user, db_password
