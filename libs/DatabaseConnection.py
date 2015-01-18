import os
import logging

from libs.ConsoleColors import *
from urllib import quote, quote_plus
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
        postgres = 'postgresql+pypostgresql://%s:%s@%s/%s' % (
            db_user, db_password, db_host, db_name,
        )
        if self._test_connection(postgres):
            return postgres
        else:
            logging.fatal("Cannot connect to database with any available driver")
            os._exit(1)

    def _sqlite(self):
        '''
        SQLite connection string, always save db file to cwd, or in-memory
        '''
        logging.debug("Configured to use SQLite for a database")
        db_name = self.database
        if not len(db_name):
            db_name = 'rtb'
        return 'sqlite:///%s.db' % db_name

    def _mysql(self):
        ''' Configure db_connection for MySQL '''
        logging.debug("Configured to use MySQL for a database")
        db_server, db_name, db_user, db_password = self._db_credentials()
        __mysql = 'mysql://%s:%s@%s/%s' % (
            db_user, db_password, db_server, db_name
        )
        __pymysql = 'mysql+pymysql://%s:%s@%s/%s' % (
            db_user, db_password, db_server, db_name
        )
        if self._test_connection(__mysql):
            return __mysql
        elif self._test_connection(__pymysql):
            logging.debug("Falling back to PyMySQL driver ...")
            return __pymysql
        else:
            logging.fatal("Cannot connect to database with any available driver")
            os._exit(1)

    def _test_connection(self, connection_string):
        '''
        Test the connection string to see if we can connect to the database
        '''
        try:
            engine = create_engine(connection_string)
            connection = engine.connect()
            connection.close()
            return True
        except:
            if options.debug:
                logging.exception("Database connection failed")
            return False

    def _db_credentials(self):
        ''' Pull db creds and return them url encoded '''
        if self.password == '' or self.password == 'RUNTIME':
            sys.stdout.write(PROMPT + "Database password: ")
            sys.stdout.flush()
            self.password = getpass.getpass()
        db_host = quote(self.hostname)
        db_name = quote(self.database)
        db_user = quote(self.username)
        db_password = quote_plus(self.password)
        return db_host, db_name, db_user, db_password
