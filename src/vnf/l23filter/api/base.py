from flask import Blueprint
from controllers.InitializeDbController import InitializeDbController
from configuration import config as cnf

base = Blueprint('base', __name__, template_folder='templates')


##########################################################
##################       DB       ########################
##########################################################


@base.route('/createDB', methods=['GET'])
def create_DB():
    initDB = InitializeDbController()

    # check if type of database is mysql or sqlite
    if cnf.DATABASE_TYPE == "mysql":
        initDB.create_DB()
        initDB.init_DB()
    elif cnf.DATABASE_TYPE == "sqlite":
        initDB.init_DB()
    return "200"

@base.route('/deleteDB', methods=['DELETE'])
def delete_DB():
    initDB = InitializeDbController()
    initDB.delete_DB()
    return "200"