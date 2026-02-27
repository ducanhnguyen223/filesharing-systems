from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.router import router as auth_router
from app.files.router import router as files_router
from app.shares.router import router as shares_router

app = FastAPI(title="FileSharing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(files_router)
app.include_router(shares_router)

@app.get("/health")
def health():
    return {"status": "ok"}
