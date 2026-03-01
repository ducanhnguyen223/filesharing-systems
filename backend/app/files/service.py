import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.models import User, File
from app.files.storage import StorageClient


def classify_mimetype(mimetype: str | None) -> str:
    if not mimetype:
        return "other"
    if mimetype.startswith("image/"):
        return "image"
    if mimetype.startswith("video/"):
        return "video"
    if mimetype.startswith("audio/"):
        return "audio"
    if mimetype.startswith("text/") or mimetype in (
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ):
        return "document"
    return "other"


def get_category_counts(user: User, db: Session) -> dict[str, int]:
    files = db.query(File).filter(File.user_id == user.id, File.is_deleted == False).all()
    counts: dict[str, int] = {"image": 0, "video": 0, "audio": 0, "document": 0, "other": 0}
    for f in files:
        counts[classify_mimetype(f.mimetype)] += 1
    return counts


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


def list_files(user: User, db: Session, category: str | None = None) -> list[File]:
    q = db.query(File).filter(File.user_id == user.id, File.is_deleted == False)
    if category:
        files = q.all()
        return [f for f in files if classify_mimetype(f.mimetype) == category]
    return q.all()


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


def bulk_delete_files(user: User, file_ids: list[int], db: Session, storage: StorageClient) -> int:
    files = (
        db.query(File)
        .filter(File.id.in_(file_ids), File.user_id == user.id, File.is_deleted == False)
        .all()
    )
    total_freed = 0
    for f in files:
        storage.delete_file(f.spaces_key)
        f.is_deleted = True
        total_freed += f.size
    user.storage_used = max(0, user.storage_used - total_freed)
    db.commit()
    return len(files)


def get_download_url(user: User, file_id: int, db: Session, storage: StorageClient) -> str:
    f = _get_file_or_404(user, file_id, db)
    return storage.get_presigned_url(f.spaces_key, expires=3600)
