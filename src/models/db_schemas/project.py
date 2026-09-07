from pydantic import BaseModel,Field,ConfigDict
from bson import ObjectId
from typing import Optional

class ProjectSchema(BaseModel):
    id: Optional[ObjectId] = Field(None,alias='_id')
    project_id: str

    model_config = ConfigDict(
            arbitrary_types_allowed=True,
            populate_by_name=True,
            json_encoders={ObjectId: str}
        )