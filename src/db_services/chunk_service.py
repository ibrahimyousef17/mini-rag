from .base_service import BaseService
from models.enums import DataBaseEnum
from models.db_schemas import ChunkSchema 
from pymongo import InsertOne
class ChunkService(BaseService):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.collection_chunk_name.value] # type: ignore

    async def create_chunk(self,chunk: ChunkSchema):
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True,exclude_unset=True))
        chunk.id = result.inserted_id
        return chunk

    async def get_chunk(self,chunk_id:str):
        result = await self.collection.find_one({
            'chunk_id':chunk_id
        })

        if result is None :
            return None 
        return ChunkSchema(**result)

    async def insert_many_chunks(self, chunks:list,batch_size:int=10):
        for i in range(0,len(chunks),batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.model_dump(by_alias=True,exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        return len(chunks)

    async def delete_chunks_by_project_id(self,project_id:str):
        result = await self.collection.delete_many({
            'project_id':project_id
        })

        return result.deleted_count

    