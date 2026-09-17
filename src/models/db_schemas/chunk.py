from pydantic import BaseModel,Field,ConfigDict
from bson import ObjectId
from typing import Optional

class ChunkSchema(BaseModel):
    id: Optional[ObjectId] = Field(None,alias='_id')
    chunk_text: str
    chunk_meta_data : dict
    chunk_id : str
    asset_id : ObjectId
    project_id: ObjectId

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

    @classmethod
    def get_indexes(cls):
        return [
            {
                'keys':[
                    ("project_id",1)
                ],
                'name':'chunk_project_id_index_1',
                'unique': False
            },
            {
                'keys':[
                    ("project_id",1),
                    ('chunk_id',1),
                    ('asset_id', 1),
                ],
                'name':"chunk_id_project_id_index_1",
                'unique':True
            },
            {
                'keys':[
                    ("asset_id",1),
                ],
                'name':"chunk_asset_id_index_1",
                'unique':False
            },

        ]