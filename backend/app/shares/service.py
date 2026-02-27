import secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.models import User, File, Share
from app.files.storage import StorageClient


def create_share(user: User, file_id: int, db: Session) -> Share:
    f = db.query(File).filter(File.id == file_id, File.user_id == user.id, File.is_deleted == False).first()
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    token = secrets.token_urlsafe(32)
    share = Share(file_id=f.id, token=token)
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


def get_share_download_url(token: str, db: Session, storage: StorageClient) -> str:
    share = db.query(Share).filter(Share.token == token).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    if share.file.is_deleted:
        raise HTTPException(status_code=404, detail="File no longer available")
    return storage.get_presigned_url(share.file.spaces_key, expires=3600)


def delete_share(user: User, share_id: int, db: Session) -> None:
    share = db.query(Share).filter(Share.id == share_id).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    if share.file.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your share")
    db.delete(share)
    db.commit()
