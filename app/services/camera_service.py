import io
import time
import math
import random
from typing import Optional, List, Generator
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from app.models.camera import Camera
from app.schemas.camera import CameraCreate
from app.websocket.manager import ws_manager

class CameraService:
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
    def generate_mjpeg_stream(camera_id: str, camera_name: str) -> Generator[bytes, None, None]:
        """
        Generates simulated high-tech tactical CCTV frames with timestamp,
        scanlines, HUD overlays, and dynamic AI detection bounding boxes.
        """
        width, height = 640, 360
        frame_idx = 0

        while True:
            frame_idx += 1
            # Base dark tactical CCTV canvas
            img = Image.new("RGB", (width, height), color=(14, 18, 24))
            draw = ImageDraw.Draw(img)

            # Draw tactical grid lines
            for x in range(40, width, 80):
                draw.line([(x, 0), (x, height)], fill=(25, 33, 44), width=1)
            for y in range(40, height, 60):
                draw.line([(0, y), (width, y)], fill=(25, 33, 44), width=1)

            # Simulated CCTV scene elements (corridor perspective)
            draw.line([(0, height), (width // 3, height // 2)], fill=(40, 52, 70), width=2)
            draw.line([(width, height), (width * 2 // 3, height // 2)], fill=(40, 52, 70), width=2)
            draw.rectangle([width // 3, height // 3, width * 2 // 3, height // 2], outline=(30, 42, 58), width=1)

            # Dynamic AI Detection scenario for CAM-002 / CAM-MOB
            t = frame_idx * 0.08
            is_fall_demo = "CAM-002" in camera_id or "MOB" in camera_id
            
            if is_fall_demo:
                # Simulate moving subject that occasionally falls
                phase = math.sin(t * 0.5)
                if phase > 0.3:
                    # Normal standing person
                    bx, by = int(280 + math.sin(t) * 40), 140
                    bw, bh = 60, 150
                    draw.rectangle([bx, by, bx + bw, by + bh], outline=(0, 220, 255), width=2)
                    draw.rectangle([bx, by - 20, bx + 110, by], fill=(0, 220, 255))
                    draw.text((bx + 4, by - 16), "PERSON 96.4%", fill=(10, 15, 20))
                else:
                    # Fallen person on ground (horizontal bounding box)
                    bx, by = 260, 250
                    bw, bh = 160, 60
                    # Red tactical alert box
                    draw.rectangle([bx, by, bx + bw, by + bh], outline=(255, 51, 75), width=3)
                    draw.rectangle([bx, by - 22, bx + 150, by], fill=(255, 51, 75))
                    draw.text((bx + 4, by - 18), "FALL DETECTED 93.2%", fill=(255, 255, 255))
            else:
                # Normal surveillance bounding box
                bx = int(220 + math.cos(t * 0.3) * 80)
                by = 160
                draw.rectangle([bx, by, bx + 55, by + 130], outline=(0, 230, 118), width=2)
                draw.rectangle([bx, by - 18, bx + 95, by], fill=(0, 230, 118))
                draw.text((bx + 4, by - 15), "SECURE 98.1%", fill=(10, 15, 20))

            # HUD Overlays: Camera Name, Timestamp, FPS, Watermark
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            draw.rectangle([10, 10, 240, 36], fill=(0, 0, 0, 180))
            draw.text((16, 14), f"REC ● {camera_id} - LIVE", fill=(255, 51, 75))
            draw.text((16, 26), f"{camera_name[:24]}", fill=(180, 200, 220))

            # Watermark / Tag
            draw.text((width - 190, 14), now_str, fill=(160, 180, 200))
            draw.text((width - 150, height - 24), "AERIS AI ENGINE v2.4", fill=(0, 220, 255))
            draw.text((16, height - 24), "SIMULATED FEED // DEMO CAMERA", fill=(255, 159, 28))

            # Encode as JPEG
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75)
            frame_bytes = buf.getvalue()

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
            time.sleep(0.08) # ~12 FPS for smooth demo streaming

camera_service = CameraService()
