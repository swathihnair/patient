# Patient Monitoring System - Backend

Python backend for real-time patient activity monitoring using MediaPipe and computer vision.

## Quick Start

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

Server will start at http://localhost:8000

## Generate Test Video

To create a sample test video:
```bash
python generate_test_video.py
```

This will create `uploads/test_patient.mp4` with simulated patient activities.

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Environment Variables

Create a `.env` file for configuration:
```
PORT=8000
HOST=0.0.0.0
UPLOAD_DIR=uploads
```

## Detection Parameters

Adjust in `main.py`:
- `fall_threshold`: Sensitivity for fall detection (default: 0.3)
- `rapid_movement_threshold`: Sensitivity for movement detection (default: 0.15)
- `frame_buffer_size`: Number of frames to analyze (default: 10)
