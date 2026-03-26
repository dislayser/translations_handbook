import sys
import os
from pathlib import Path

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импортируем модули
try:
    from app.api import public, admin
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Files in current dir: {os.listdir('.')}")
    if os.path.exists('app'):
        print(f"Files in app dir: {os.listdir('app')}")
    if os.path.exists('app/api'):
        print(f"Files in app/api dir: {os.listdir('app/api')}")
    raise

app = FastAPI(
    title="Translation Service API",
    description="Multi-language translation service with Redis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(public.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {
        "service": "Translation Service",
        "version": "1.0.0",
        "endpoints": {
            "public": "/api/public",
            "admin": "/api/admin"
        }
    }

@app.get("/health")
async def health_check():
    from app.redis_client import redis_client
    try:
        redis_client.client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": str(e)}