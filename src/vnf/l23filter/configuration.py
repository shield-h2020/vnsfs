import os
import configparser
import getpass


class config:

    # --------------------------  Global Variables  -----------------------------
    # Base Directory
    BASE_DIR = os.path.dirname(__file__)
    BASE_USER_DIR = os.path.join("/home", getpass.getuser())

    # Configuration File Directory
    CONF_FILE_DIR = os.path.join("main.conf")

    config = configparser.ConfigParser()
    config.read(CONF_FILE_DIR)


    # -------------------------- Default --------------------------------------------

    # Server Port
    PORT = int(config['DEFAULT']['port'])

    # -------------------------- Database -------------------------------------------

    DATABASE_TYPE = config['DATABASE']['type']
    DATABASE_PATH = os.path.join(BASE_DIR, "db", config['DATABASE']['name'])
    DATABASE_CONN_STRING = config['DATABASE']['conn_string']
    DATABASE_NAME = config['DATABASE']['name']


    # -------------------------- Traffic Control -------------------------------------------

    TRAFFIC_CONTROL_IFACE = config['TRAFFIC_CONTROL']['interface']
    TRAFFIC_CONTROL_UNIV_BURST_LIMIT = config['TRAFFIC_CONTROL']['universal_burst_limit']

