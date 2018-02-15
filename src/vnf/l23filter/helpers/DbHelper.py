from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker
from configuration import config as cnf

Session = sessionmaker()

def on_connect(conn, record):
    conn.execute('pragma foreign_keys=ON')


def assert_database_type():
    # Check if type of DB is sqlite or mysql
    connection_string = None
    # empty string
    engine = None

    if cnf.DATABASE_TYPE == "mysql":
        connection_string = "mysql" + cnf.DATABASE_CONN_STRING + "/" + cnf.DATABASE_NAME
        engine = create_engine(connection_string)
    elif cnf.DATABASE_TYPE == "sqlite":
        connection_string = "sqlite:///" + cnf.DATABASE_PATH
        engine = create_engine(connection_string)
        event.listen(engine, 'connect', on_connect)
    print(connection_string)

    return engine

@contextmanager
def db_session():
    """ Creates a context with an open SQLAlchemy session.
    """
    engine = assert_database_type()

    connection = engine.connect()
    db_sess = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
    yield db_sess
    db_sess.remove()
    connection.close()
