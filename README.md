# AERIS Backend & AI Engine

High-performance asynchronous FastAPI backend providing real-time emergency detection routing, spatial responder dispatching (Haversine formula), WebSocket broadcast gateway, and simulated AI video analytics.

## Features
- **FastAPI + Asynchronous Handlers**: Sub-millisecond response times.
- **WebSocket Gateway (`/ws/{client_id}`)**: Instant bi-directional event broadcasts.
- **Spatial Responder Matching**: Haversine distance geofencing with availability filtering.
- **Modular AI Engine**: Fall detection (pose & velocity), fire/smoke optical classifier, crowd density estimator.
- **MJPEG Stream Generation**: Built-in canvas video stream simulator with real-time HUD and AI bounding boxes.
- **Self-Healing SQLite / Supabase Support**: Zero-config auto-seeding on launch.

## Quick Start

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation available at:
`http://localhost:8000/docs`
