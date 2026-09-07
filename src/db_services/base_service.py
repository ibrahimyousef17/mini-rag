from helpers.config import get_settings


class BaseService():
    def __init__(self,db_client : object):
        self.settings = get_settings()
        self.db_client = db_client