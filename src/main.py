from fastapi import FastAPI

from src.domain.routing.parcel import router as parcel_router

app = FastAPI(
    title="Delivery Service API",
    description="API для международной службы доставки посылок",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(parcel_router)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Delivery Service API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["root"])
async def health_check():
    return {"status": "healthy"}
