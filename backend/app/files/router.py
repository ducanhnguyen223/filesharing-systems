from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.router import get_current_user_dep
from app.files.storage import StorageClient, get_storage_client
from app.files import schemas, service

router = APIRouter(prefix="/files", tags=["files"])


def get_storage_dep() -> StorageClient:
    return get_storage_client()


@router.post("/upload", response_model=schemas.FileResponse)
def upload(
    file: UploadFile = FastAPIFile(...),
    user=Depends(get_current_user_dep),
    db: Session = Depends(get_db),
    storage: StorageClient = Depends(get_storage_dep),
):
    return service.upload_file(user, file, db, storage)


@router.get("/", response_model=schemas.FileListResponse)
def list_files(
    category: str | None = Query(default=None, description="Filter by category: image, video, audio, document, other"),
    user=Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    files = service.list_files(user, db, category=category)
    counts = service.get_category_counts(user, db)
    return {"files": files, "total": len(files), "category_counts": counts}


@router.get("/{file_id}/download")
def download(
    file_id: int,
    user=Depends(get_current_user_dep),
    db: Session = Depends(get_db),
    storage: StorageClient = Depends(get_storage_dep),
):
    url = service.get_download_url(user, file_id, db, storage)
    return {"url": url}


@router.delete("/{file_id}", status_code=204)
def delete(
    file_id: int,
    user=Depends(get_current_user_dep),
    db: Session = Depends(get_db),
    storage: StorageClient = Depends(get_storage_dep),
):
    service.delete_file(user, file_id, db, storage)
