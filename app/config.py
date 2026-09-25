import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "AERIS - AI Emergency Response & Intelligent Surveillance"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "aeris-tactical-secret-key-2026-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aeris.db")
    
    # Emergency Response parameters
    DEFAULT_DISPATCH_RADIUS_METERS: float = 1000.0 # 1 km search radius
    MAX_NOTIFIED_RESPONDERS: int = 5
    
    # Campus reference GPS coordinates (Bangalore Tech Campus demo center)
    DEFAULT_CENTER_LAT: float = 12.9716
    DEFAULT_CENTER_LON: float = 77.5946

settings = Settings()
