from typing import List
from datetime import datetime, timedelta, timezone
import io
import secrets
import qrcode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraResponse, CameraPairRequest, PairingSessionResponse, PairingStatusResponse
from app.services.camera_service import camera_service

router = APIRouter(prefix="/cameras", tags=["Cameras"])
pairing_sessions: dict[str, dict] = {}

def resolve_api_base_url(request: Request) -> str:
    custom_base = request.headers.get("x-api-base-url")
    if custom_base:
        base = custom_base.strip().rstrip("/")
        return base if base.endswith("/api/v1") else f"{base}/api/v1"

    forwarded_host = request.headers.get("x-forwarded-host")
    if forwarded_host:
        forwarded_proto = request.headers.get("x-forwarded-proto", "http")
        host = forwarded_host.split(",")[0].strip()
        return f"{forwarded_proto}://{host.rstrip('/')}/api/v1"

    return f"{str(request.base_url).rstrip('/')}/api/v1"


def get_session(token: str) -> dict:
    session = pairing_sessions.get(token)
    if not session or session["expires_at"] < datetime.now(timezone.utc):
        pairing_sessions.pop(token, None)
        raise HTTPException(status_code=404, detail="Pairing code is invalid or expired")
    return session

@router.get("", response_model=List[CameraResponse])
def get_cameras(db: Session = Depends(get_db)):
    return camera_service.get_all_cameras(db)

@router.post("/register", response_model=CameraResponse)
def register_camera(camera_in: CameraCreate, db: Session = Depends(get_db)):
    return camera_service.register_camera(db, camera_in)

@router.get("/{id}", response_model=CameraResponse)
def get_camera(id: str, db: Session = Depends(get_db)):
    cam = camera_service.get_camera_by_id(db, id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam

@router.post("/{id}/connect", response_model=CameraResponse)
async def connect_camera(id: str, db: Session = Depends(get_db)):
    cam = await camera_service.connect_camera(db, id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam

@router.post("/{id}/disconnect", response_model=CameraResponse)
async def disconnect_camera(id: str, db: Session = Depends(get_db)):
    cam = await camera_service.disconnect_camera(db, id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam

@router.post("/pairing-sessions", response_model=PairingSessionResponse)
def create_pairing_session(request: Request):
    token = secrets.token_urlsafe(24)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    api_url = resolve_api_base_url(request)
    pairing_sessions[token] = {"expires_at": expires_at, "camera": None, "api_url": api_url}
    return PairingSessionResponse(token=token, qr_image_url=f"/cameras/pairing-sessions/{token}/qr", expires_at=expires_at)

@router.get("/pairing-sessions/{token}/qr")
def pairing_qr(token: str):
    get_session(token)
    image = qrcode.make(f"AERIS_PAIR:{get_session(token)['api_url']}|{token}")
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return StreamingResponse(output, media_type="image/png", headers={"Cache-Control": "no-store"})

@router.get("/pairing-sessions/{token}", response_model=PairingStatusResponse)
def pairing_status(token: str):
    session = get_session(token)
    return PairingStatusResponse(status="PAIRED" if session["camera"] else "WAITING", camera=session["camera"])

@router.post("/pair", response_model=CameraResponse)
async def pair_camera(pair_in: CameraPairRequest, db: Session = Depends(get_db)):
    session = get_session(pair_in.token)
    camera_id = f"MOB-{secrets.token_hex(4).upper()}"
    cam = camera_service.register_camera(db, CameraCreate(
        id=camera_id,
        name=pair_in.device_name.strip()[:255] or "Android mobile camera",
        type="MOBILE",
        location_name="Mobile Responder Unit",
        latitude=pair_in.latitude,
        longitude=pair_in.longitude,
        status="STREAMING",
        ai_enabled=True,
    ))
    await camera_service.connect_camera(db, cam.id)
    session["camera"] = cam
    return cam

@router.get("/{id}/stream")
def stream_camera(id: str, db: Session = Depends(get_db)):
    cam = camera_service.get_camera_by_id(db, id)
    cam_name = cam.name if cam else id
    return StreamingResponse(
        camera_service.generate_mjpeg_stream(id, cam_name),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
