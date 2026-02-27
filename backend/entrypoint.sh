#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
  sleep 1
done
echo "Database ready."

echo "Running migrations..."
alembic upgrade head

echo "Seeding plans..."
python -c "
from app.core.database import SessionLocal
from app.core.models import Plan

db = SessionLocal()
if not db.query(Plan).filter(Plan.name == 'free').first():
    db.add(Plan(name='free', storage_limit=5*1024**3, file_size_limit=100*1024**2, price_monthly=0))
if not db.query(Plan).filter(Plan.name == 'pro').first():
    db.add(Plan(name='pro', storage_limit=50*1024**3, file_size_limit=1024**3, price_monthly=9.99))
db.commit()
db.close()
print('Plans seeded.')
"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
