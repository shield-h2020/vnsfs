import logging

from sqlalchemy import create_engine, event

from configuration import config as cnf
from helpers.DbHelper import on_connect, db_session, assert_database_type
from models import Base, Flow
# from models.depreciated import Metric

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)



class InitializeDbController:

    def create_DB(self):

        mysqldbType = "mysql"
        connection_string = None
        # empty string
        connection_string = mysqldbType + cnf.DATABASE_CONN_STRING
        print(connection_string)
        # if connection_string.startswith('sqlite'):
        #     db_file = re.sub("sqlite.*:///", "", connection_string)
        #     os.makedirs(os.path.dirname(db_file))
        engine = create_engine(connection_string, echo=False)
        # event.listen(engine, 'connect', on_connect)
        conn = engine.connect()
        conn.execute("commit")
        conn.execute("CREATE DATABASE IF NOT EXISTS test;")

        conn.close()

    def init_DB(self):


        # if connection_string.startswith('sqlite'):
        #     db_file = re.sub("sqlite.*:///", "", connection_string)
        #     os.makedirs(os.path.dirname(db_file))

        # 3 commands for creating database

        base = Base.Base()
        Flow.Flow()

        engine = assert_database_type()
        base.metadata.create_all(engine)


        response = "OK"
        return response


    def delete_DB(self):

        engine = assert_database_type()

        base = Base.Base()
        for tbl in reversed(base.metadata.sorted_tables):
            tbl.drop(engine, checkfirst=True)

