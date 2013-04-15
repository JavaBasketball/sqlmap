#!/usr/bin/env python

"""
Copyright (c) 2006-2013 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import imp
import sys

_sqlalchemy = None
try:
    f, pathname, desc = imp.find_module("sqlalchemy", sys.path[1:])
    _sqlalchemy = imp.load_module("sqlalchemy", f, pathname, desc)
except ImportError:
    pass

from lib.core.data import conf
from lib.core.data import logger
from lib.core.exception import SqlmapConnectionException
from plugins.generic.connector import Connector as GenericConnector

class SQLAlchemy(GenericConnector):
    def __init__(self, dialect=None):
        GenericConnector.__init__(self)

        self.dialect = dialect

    def connect(self):
        if _sqlalchemy:
            self.initConnection()

            try:
                if not self.port and self.db:
                    if "///" not in conf.direct:
                        conf.direct = conf.direct.replace("//", "///", 1)
                if self.dialect:
                    conf.direct = conf.direct.replace(conf.dbms, self.dialect)
                engine = _sqlalchemy.create_engine(conf.direct, connect_args={'check_same_thread':False} if self.dialect == "sqlite" else {})
                self.connection = engine.connect()
            except Exception, msg:
                raise SqlmapConnectionException(msg[0])

            self.printConnected()

    def fetchall(self):
        try:
            return self.cursor.fetchall()
        except _sqlalchemy.exc.ProgrammingError, msg:
            logger.log(logging.WARN if conf.dbmsHandler else logging.DEBUG, "(remote) %s" % msg[1])
            return None

    def execute(self, query):
        try:
            self.cursor = self.connection.execute(query)
        except (_sqlalchemy.exc.OperationalError, _sqlalchemy.exc.ProgrammingError), msg:
            logger.log(logging.WARN if conf.dbmsHandler else logging.DEBUG, "(remote) %s" % msg[1])
        except _sqlalchemy.exc.InternalError, msg:
            raise SqlmapConnectionException(msg[1])

    def select(self, query):
        self.execute(query)
        return self.fetchall()