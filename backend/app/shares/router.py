from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.router import get_current_user_dep
from app.files.router import get_storage_dep
from app.files.storage import StorageClient
from app.shares import schemas, service

router = APIRouter(prefix="/shares", tags=["shares"])


@router.post("/", response_model=schemas.ShareResponse)
def create_share(
    data: schemas.ShareRequest,
    request: Request,
    user=Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    share = service.create_share(user, data.file_id, db)
    share_url = str(request.base_url) + f"shares/{share.token}"
    return schemas.ShareResponse(
        id=share.id,
        token=share.token,
        file_id=share.file_id,
        expires_at=share.expires_at,
        created_at=share.created_at,
        share_url=share_url,
    )


@router.get("/{token}")
def public_download(
    token: str,
    db: Session = Depends(get_db),
    storage: StorageClient = Depends(get_storage_dep),
):
    url = service.get_share_download_url(token, db, storage)
    return RedirectResponse(url=url)


@router.delete("/{share_id}", status_code=204)
def delete_share(
    share_id: int,
    user=Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    service.delete_share(user, share_id, db)
