from pydantic import BaseModel, ConfigDict,Field
from typing import Optional 
from bson import ObjectId
from datetime import datetime
class AssetSchema(BaseModel):
    
    id: Optional[ObjectId] = Field(None,alias='_id')
    asset_project_id:ObjectId
    asset_hash:str
    asset_name:str
    asset_type:str 
    asset_size:int = Field(default=None,gt=0) # type: ignore
    asset_status:str = Field(default='Panding')
    asset_pushed_at: datetime = Field(default=datetime.now) # type: ignore
    asset_config: dict = Field(default=None) # type: ignore

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
                    ('asset_project_id',1),
                ],
                'name':'asset_project_id_1',
                'unique':False
            },
            {
                'keys':[
                    ('asset_project_id',1),
                    ('asset_name',1),
                ],
                'name':'asset_project_id_asset_name_1',
                'unique':True
            },
            {
                'keys':[
                    ('asset_hash',1)
                ],
                'name':'asset_hash_index_1',
                'unique':True
            }
        ]
    