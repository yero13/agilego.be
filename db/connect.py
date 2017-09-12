from pymongo import MongoClient
import logging
import json


class MongoDb:
    # ToDo: implement pooling and singleton for connections
    __CFG_DB_CONNECT = './cfg/db.json'
    __CFG_PARAM_MONGO_DBNAME = 'MONGO_DBNAME'
    __CFG_PARAM_MONGO_HOST = 'MONGO_HOST'
    __CFG_PARAM_MONGO_PORT = 'MONGO_PORT'
    __CFG_PARAM_MONGO_USER = 'MONGO_USER'
    __CFG_PARAM_MONGO_PSWD = 'MONGO_PASSWORD'

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        with open(MongoDb.__CFG_DB_CONNECT) as cfg_file:
            __cfg = json.load(cfg_file, strict=False)
        self.__connection = MongoClient('mongodb://{}:{}@{}:{:d}/'.format(__cfg[MongoDb.__CFG_PARAM_MONGO_USER],
                                                                         __cfg[MongoDb.__CFG_PARAM_MONGO_PSWD],
                                                                         __cfg[MongoDb.__CFG_PARAM_MONGO_HOST],
                                                                         __cfg[MongoDb.__CFG_PARAM_MONGO_PORT]))[__cfg[MongoDb.__CFG_PARAM_MONGO_DBNAME]]
        self.__logger.debug('Mongo connection - instantiation')

    @property
    def connection(self):
        return self.__connection
        self.__logger.debug('Mongo connection - getting')