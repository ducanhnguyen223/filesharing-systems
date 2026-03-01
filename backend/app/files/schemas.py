from pydantic import BaseModel, computed_field
from datetime import datetime
from app.files.service import classify_mimetype


class FileResponse(BaseModel):
    id: int
    filename: str
    size: int
    mimetype: str | None
    spaces_key: str
    created_at: datetime

    @computed_field
    @property
    def category(self) -> str:
        return classify_mimetype(self.mimetype)

    model_config = {"from_attributes": True}


class FileListResponse(BaseModel):
    files: list[FileResponse]
    total: int
    category_counts: dict[str, int] = {}


class BulkDeleteRequest(BaseModel):
    file_ids: list[int]


class BulkDeleteResponse(BaseModel):
    deleted: int
