from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import auth
from app.api import user, role, permission
from app.api.log import router as log_router
from app.middleware.api_log import ApiLogMiddleware
from app.middleware.api_auth import ApiAuthMiddleware
from app.db.database import create_tables
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Execute on startup
    create_tables()
    print("🚀 FastAPI application started successfully!")
    print(f"📚 API documentation URL: http://localhost:8000/docs")
    
    yield
    
    # Execute on shutdown (if needed)
    print("👋 FastAPI application is shutting down...")


# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A FastAPI example project with JWT authentication",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Register API log middleware (logs all non-GET requests)
app.add_middleware(ApiLogMiddleware)

# Register auth middleware (requires JWT for all routes except /auth/*)
app.add_middleware(ApiAuthMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should set specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/users", tags=["usermgt"])
app.include_router(role.router, prefix="/api/roles", tags=["rolemgt"])
app.include_router(permission.router, prefix="/api/permissions", tags=["permissionmgt"])
app.include_router(log_router, prefix="/api/logs", tags=["logs"])


@app.get("/")
async def root():
    """Root path"""
    return {
        "message": "Welcome to FastAPI JWT authentication example project",
        "docs": "/docs",
        "redoc": "/redoc"
    }





@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )