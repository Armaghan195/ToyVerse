
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.database import check_db_connection
from app.api.routes import auth, products, cart, orders, reviews, admin, uploads, chatbot, recommendations, support, wishlist, profile
from fastapi.staticfiles import StaticFiles

logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_application() -> FastAPI:

    app = FastAPI(
        title=settings.app_name,
        description="A comprehensive e-commerce backend demonstrating OOP principles",
        version="1.0.0",
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix=settings.api_v1_prefix)
    app.include_router(profile.router, prefix=settings.api_v1_prefix)
    app.include_router(products.router, prefix=settings.api_v1_prefix)
    app.include_router(cart.router, prefix=settings.api_v1_prefix)
    app.include_router(orders.router, prefix=settings.api_v1_prefix)
    app.include_router(reviews.router, prefix=settings.api_v1_prefix)
    app.include_router(admin.router, prefix=settings.api_v1_prefix)
    app.include_router(uploads.router, prefix=settings.api_v1_prefix)
    app.include_router(chatbot.router, prefix=settings.api_v1_prefix)
    app.include_router(recommendations.router, prefix=settings.api_v1_prefix)
    app.include_router(support.router, prefix=settings.api_v1_prefix)
    app.include_router(wishlist.router, prefix=settings.api_v1_prefix)

    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    return app

app = create_application()

@app.on_event("startup")
async def startup_event():

    logger.info(f"Starting {settings.app_name}...")

    if check_db_connection():
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed!")

    logger.info(f"{settings.app_name} started successfully")

@app.on_event("shutdown")
async def shutdown_event():

    logger.info(f"Shutting down {settings.app_name}...")

@app.get("/")
async def root():

    return {
        "message": "Welcome to ToyVerse API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():

    db_healthy = check_db_connection()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": "1.0.0"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):

    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
