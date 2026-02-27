from pydantic import BaseModel
from datetime import datetime


class ShareRequest(BaseModel):
    file_id: int


class ShareResponse(BaseModel):
    id: int
    token: str
    file_id: int
    expires_at: datetime | None
    created_at: datetime
    share_url: str

    model_config = {"from_attributes": True}
