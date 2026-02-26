# FileSharing System — Design Document
**Date:** 2026-02-24
**Status:** Approved

---

## Overview

Mini Google Drive — sản phẩm hoàn chỉnh, public, deploy trên DigitalOcean.
Người dùng có thể đăng ký, upload/download file, và tạo share link công khai.
Có Free tier và Paid tier để kiểm soát chi phí storage.

**Không dùng microservices** — monolith có cấu trúc module rõ ràng, dễ maintain và dễ scale sau.

---

## Phần 1: Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────┐
│                   Browser / Client                   │
└───────────────────┬─────────────────────────────────┘
                    │ HTTP/HTTPS
┌───────────────────▼─────────────────────────────────┐
│              Vue.js SPA (Frontend)                   │
│         (host trên DO App Platform)                  │
└───────────────────┬─────────────────────────────────┘
                    │ REST API
┌───────────────────▼─────────────────────────────────┐
│              FastAPI App (Backend)                   │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐ │
│  │  auth    │ │  files   │ │ shares │ │ billing  │ │
│  │ module   │ │  module  │ │ module │ │  module  │ │
│  └──────────┘ └──────────┘ └────────┘ └──────────┘ │
│         (host trên DO App Platform)                  │
└──────────┬──────────────────────┬────────────────────┘
           │                      │
┌──────────▼──────────┐  ┌────────▼───────────────────┐
│  DO Managed         │  │  DigitalOcean Spaces        │
│  PostgreSQL         │  │  (S3-compatible storage)    │
│  (metadata, users,  │  │  (file blobs thực tế)       │
│   plans, shares)    │  │                             │
└─────────────────────┘  └────────────────────────────┘
```

**CI/CD Pipeline:**
```
GitHub push → GitHub Actions → Run tests → Build Docker image
           → Push to DO Container Registry → Deploy to App Platform
```

---

## Phần 2: Database Schema & Features

### Database Schema (PostgreSQL)

```sql
users
  id, email, password_hash, created_at
  plan_id (FK → plans)
  storage_used (bytes)

plans
  id, name ("free"/"pro"), storage_limit (bytes), price_monthly

files
  id, user_id (FK), filename, size, mimetype
  spaces_key (path trong DO Spaces)
  created_at, is_deleted

shares
  id, file_id (FK), token (unique random string)
  expires_at (nullable), created_at
```

### Features V1

| Feature | Mô tả |
|---|---|
| Đăng ký / Đăng nhập | Email + password, JWT access token |
| Upload file | Giới hạn theo plan quota |
| List files | Xem danh sách file của mình |
| Download file | Download về máy |
| Delete file | Xóa file, giải phóng quota |
| Tạo share link | Link public `/share/{token}` ai cũng mở được |
| Xem plan | Biết mình đang dùng bao nhiêu storage |

**Không có trong V1** (để sau): preview file, folder, share có password, payment thật (Stripe), collaborative, AI features.

### Storage Tiers

| Plan | Storage tổng | Upload tối đa/file | Giá |
|---|---|---|---|
| Free | 5 GB | 100 MB | Miễn phí |
| Pro | 50 GB | 1 GB | Trả phí (admin set tay V1) |

---

## Phần 3: Tech Stack & Project Structure

### Tech Stack

| Layer | Công nghệ | Lý do |
|---|---|---|
| Backend | FastAPI (Python) | Async, nhanh, phù hợp Python skill |
| Frontend | Vue.js 3 + Vite | Đã có kinh nghiệm |
| Database | DO Managed PostgreSQL | Managed, backup tự động |
| File Storage | DO Spaces | S3-compatible, rẻ, CDN sẵn |
| Auth | JWT (python-jose) | Stateless, đơn giản |
| ORM | SQLAlchemy + Alembic | Migration rõ ràng |
| Deploy | DO App Platform | Tự scale, không cần quản lý server |
| CI/CD | GitHub Actions | Quen từ project cũ |
| Container | Docker | Đóng gói nhất quán |

### Cấu trúc thư mục

```
filesharing-system/
├── backend/
│   ├── app/
│   │   ├── auth/          # register, login, JWT
│   │   ├── files/         # upload, download, list, delete
│   │   ├── shares/        # tạo & truy cập share link
│   │   ├── billing/       # plan, quota check
│   │   ├── core/          # config, database, security
│   │   └── main.py
│   ├── alembic/           # DB migrations
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/         # Login, Dashboard, SharePage
│   │   ├── components/
│   │   └── api/           # axios calls
│   ├── Dockerfile
│   └── vite.config.js
├── .github/
│   └── workflows/
│       └── deploy.yml     # test → build → push → deploy
└── docker-compose.yml     # local dev only
```

### CI/CD Flow

```
git push main
    ↓
GitHub Actions:
  1. Run pytest (backend tests)
  2. Build Docker images
  3. Push to DO Container Registry
  4. Trigger App Platform redeploy
    ↓
Live tại: https://yourapp.ondigitalocean.app
```

### Chi phí DigitalOcean (ước tính)

| Service | Chi phí |
|---|---|
| App Platform (backend + frontend) | ~$12/tháng |
| Managed PostgreSQL (basic) | ~$15/tháng |
| Spaces (250GB + CDN) | ~$5/tháng |
| Container Registry | Free tier |
| **Tổng** | **~$32/tháng** |

Nằm trong GitHub Student Pack credit của DigitalOcean.

---

## Roadmap sau V1

- **V2**: Preview file (ảnh, PDF), folder, share link có thời hạn/password
- **V3**: Tích hợp payment thật (Stripe) cho Pro plan
- **V4**: AI features — gợi ý tổ chức file, tìm kiếm bằng ngôn ngữ tự nhiên, auto-tag
