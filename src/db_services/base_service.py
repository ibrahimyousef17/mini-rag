from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorDatabase

class BaseService():
    def __init__(self,db_client : AsyncIOMotorDatabase):
        self.settings = get_settings()
        self.db_client = db_client