from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import patients, synthesize, chat, appointments
from app.db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Amani Clinical Intake API",
    description="Virtual Clinic MVP for synthesizing patient narratives with historical data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router, prefix="/api", tags=["patients"])
app.include_router(synthesize.router, prefix="/api", tags=["synthesis"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(appointments.router, prefix="/api", tags=["appointments"])


@app.get("/")
def read_root():
    return {
        "message": "Amani Clinical Intake API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
