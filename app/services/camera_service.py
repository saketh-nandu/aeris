import io
import time
import random
from typing import Optional, List, Generator, Dict
from datetime import datetime, timezone
from PIL import Image, ImageDraw
from sqlalchemy.orm import Session

from app.models.camera import Camera
from app.schemas.camera import CameraCreate
from app.websocket.manager import ws_manager

class CameraService:
    _live_frames: Dict[str, bytes] = {}

    @staticmethod
    def get_all_cameras(db: Session) -> List[Camera]:
        return db.query(Camera).all()

    @staticmethod
    def get_camera_by_id(db: Session, camera_id: str) -> Optional[Camera]:
        return db.query(Camera).filter(Camera.id == camera_id).first()

    @staticmethod
    def register_camera(db: Session, camera_in: CameraCreate) -> Camera:
        cam_id = camera_in.id or f"CAM-{random.randint(100, 999)}"
        camera = Camera(
            id=cam_id,
            name=camera_in.name,
            type=camera_in.type,
            location_name=camera_in.location_name,
            latitude=camera_in.latitude,
            longitude=camera_in.longitude,
            status=camera_in.status,
            stream_url=camera_in.stream_url,
            ai_enabled=camera_in.ai_enabled,
            fps=camera_in.fps,
            resolution=camera_in.resolution
        )
        db.add(camera)
        db.commit()
        db.refresh(camera)
        return camera

    @staticmethod
    async def connect_camera(db: Session, camera_id: str) -> Optional[Camera]:
        cam = db.query(Camera).filter(Camera.id == camera_id).first()
        if cam:
            cam.status = "STREAMING" if cam.type == "MOBILE" else "ONLINE"
            db.commit()
            db.refresh(cam)
            await ws_manager.broadcast("CAMERA_CONNECTED", {
                "camera_id": cam.id,
                "name": cam.name,
                "status": cam.status,
                "type": cam.type,
                "location_name": cam.location_name
            })
        return cam

    @staticmethod
    async def disconnect_camera(db: Session, camera_id: str) -> Optional[Camera]:
        cam = db.query(Camera).filter(Camera.id == camera_id).first()
        if cam:
            cam.status = "OFFLINE"
            db.commit()
            db.refresh(cam)
            await ws_manager.broadcast("CAMERA_DISCONNECTED", {
                "camera_id": cam.id,
                "status": "OFFLINE"
            })
        return cam

    @staticmethod
    def store_live_frame(camera_id: str, frame: bytes) -> None:
        if not frame:
            return
        CameraService._live_frames[camera_id] = frame

    @staticmethod
    def get_latest_frame(camera_id: str) -> Optional[bytes]:
        return CameraService._live_frames.get(camera_id)

    @staticmethod
    def reset_live_stream(camera_id: str) -> None:
        CameraService._live_frames.pop(camera_id, None)

    @staticmethod
    def generate_mjpeg_stream(camera_id: str, camera_name: str, max_frames: Optional[int] = None) -> Generator[bytes, None, None]:
        """
        Streams the most recently uploaded live frame from the mobile app.
        If no frame has been uploaded yet, a lightweight placeholder is used.
        """
        frame_count = 0

        while True:
            latest_frame = CameraService.get_latest_frame(camera_id)
            if latest_frame:
                frame_bytes = latest_frame
            else:
                width, height = 640, 360
                img = Image.new("RGB", (width, height), color=(8, 12, 18))
                draw = ImageDraw.Draw(img)
                draw.rectangle([0, 0, width, height], outline=(38, 52, 68), width=2)
                draw.text((20, 20), f"{camera_name[:24]}", fill=(200, 220, 240))
                draw.text((20, 60), "WAITING FOR LIVE CAMERA FEED", fill=(72, 192, 255))
                draw.text((20, height - 30), "AERIS LIVE STREAM", fill=(180, 200, 220))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=70)
                frame_bytes = buf.getvalue()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                return
            time.sleep(0.15)

camera_service = CameraService()
