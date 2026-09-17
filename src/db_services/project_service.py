from .base_service import BaseService 
from models.enums import DataBaseEnum
from models.db_schemas import ProjectSchema
from motor.motor_asyncio import AsyncIOMotorDatabase

class ProjectService(BaseService):
    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.collection_project_name.value]  

    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.collection_project_name.value not in all_collection:
            self.collection = self.db_client[DataBaseEnum.collection_project_name.value]  
            indexes = ProjectSchema.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    keys=index['keys'],
                    name=index['name'],
                    unique=index['unique'],
                )
                
    @classmethod
    async def create_instance(cls,db_client:AsyncIOMotorDatabase):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def create_project(self,project : ProjectSchema):
        result = await self.collection.insert_one(project.model_dump(by_alias=True,exclude_unset=True)) 
        project.id = result.inserted_id
        return project

    async def get_project_or_create_one(self,project_id:str):
        record = await self.collection.find_one(
            {
                "project_id": project_id
            }
        )

        if record is None:
            project = ProjectSchema(project_id=project_id) # type: ignore
            project = await self.create_project(project=project)
            return project
        return ProjectSchema(**record)

    async def get_all_projects(self,page:int=1,page_size:int=10):
        total_documents = await self.collection.count_documents({})

        total_pages = total_documents // page_size 

        if total_documents % page_size > 0 : 
            total_pages += 1 

        cursor =  self.collection.find().skip((page-1)*page_size).limit(page_size)

        projects = []

        async for doc in cursor:
            projects.append(
                ProjectSchema(**doc)
            )

        return projects,total_pages


    