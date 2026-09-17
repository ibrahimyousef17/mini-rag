from .base_service import BaseService
from models.enums import DataBaseEnum
from models.db_schemas import AssetSchema 
from pymongo import InsertOne
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

class AssetService(BaseService):

    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        self.collection =  self.db_client[DataBaseEnum.collection_asset_name.value]

    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.collection_asset_name.value not in all_collection:
            self.collection =  self.db_client[DataBaseEnum.collection_asset_name.value]
            indexes = AssetSchema.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    keys=index['keys'],
                    name=index['name'],
                    unique=index['unique']
                )

    @classmethod
    async def create_instance(cls,db_client: AsyncIOMotorDatabase):
        instance = cls(db_client)
        await instance.init_collection()
        return instance 

    async def create_asset(self,asset:AssetSchema):
        result = await self.collection.insert_one(asset.model_dump(by_alias=True,exclude_unset=True))
        asset.id = result.inserted_id
        return  asset 

    async def get_all_asset_by_type_and_project_id(self,project_id:str,asset_type:str):
        records = await self.collection.find(
            {
                "asset_project_id":ObjectId(project_id) if isinstance(project_id,str) else project_id ,
                "asset_type": asset_type
            }
        ).to_list(length=None)
        records = [ AssetSchema(**record)
            for record in records
        ]
        return records 

    async def get_specific_asset(self,project_id:str,asset_name:str):
        record = await self.collection.find_one({
                    "asset_project_id":ObjectId(project_id) if isinstance(project_id,str) else project_id ,
                    'asset_name':asset_name
                })
        if record :
            return AssetSchema(**record)
        return None 
    
    async def search_asset_by_hash(self,asset_hash:str):
        record = await self.collection.find_one({
            'asset_hash':asset_hash
        })
        if record :
            return AssetSchema(**record)
        return None 

    async def update_asset_status(self,asset_name:str,asset_status:str):
        result = await self.collection.update_one(
            
                {'asset_name':asset_name},
                {'$set':{'asset_status':asset_status}}
            
        )
        return result 

    async def reset_project_asset_status(self,project_id:str,asset_status:str):
        result = await self.collection.update_many(
                        {'asset_project_id':ObjectId(project_id) if isinstance(project_id,str) else project_id},
                        {'$set':{'asset_status':asset_status}}
                    
                )
        return result 