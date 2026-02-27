import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.models import User, File
from app.files.storage import StorageClient


def upload_file(user: User, file: UploadFile, db: Session, storage: StorageClient) -> File:
    content = file.file.read()
    size = len(content)

    if size > user.plan.file_size_limit:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Limit: {user.plan.file_size_limit // (1024**2)}MB",
        )
    if user.storage_used + size > user.plan.storage_limit:
        raise HTTPException(status_code=400, detail="Storage quota exceeded")

    key = f"{user.id}/{uuid.uuid4()}/{file.filename}"
    import io
    storage.upload_file(io.BytesIO(content), key, file.content_type or "application/octet-stream")

    db_file = File(
        user_id=user.id,
        filename=file.filename,
        size=size,
        mimetype=file.content_type,
        spaces_key=key,
    )
    db.add(db_file)
    user.storage_used += size
    db.commit()
    db.refresh(db_file)
    return db_file


def list_files(user: User, db: Session) -> list[File]:
    return db.query(File).filter(File.user_id == user.id, File.is_deleted == False).all()


def _get_file_or_404(user: User, file_id: int, db: Session) -> File:
    f = db.query(File).filter(File.id == file_id, File.user_id == user.id, File.is_deleted == False).first()
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    return f


def delete_file(user: User, file_id: int, db: Session, storage: StorageClient) -> None:
    f = _get_file_or_404(user, file_id, db)
    storage.delete_file(f.spaces_key)
    f.is_deleted = True
    user.storage_used = max(0, user.storage_used - f.size)
    db.commit()


def get_download_url(user: User, file_id: int, db: Session, storage: StorageClient) -> str:
    f = _get_file_or_404(user, file_id, db)
    return storage.get_presigned_url(f.spaces_key, expires=3600)
