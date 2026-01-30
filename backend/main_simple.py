from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from datetime import datetime
from typing import List
import asyncio
import aiofiles
import os
from pathlib import Path

app = FastAPI(title="Patient Monitoring System")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class ActivityDetector:
    """Simple activity detector using OpenCV without MediaPipe for now"""
    def __init__(self):
        self.prev_frames = []
        self.fall_threshold = 0.3
        self.rapid_movement_threshold = 30.0  # Pixel movement threshold
        self.frame_buffer_size = 10
        
    def detect_movement(self, frame):
        """Detect movement using frame differencing"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        self.prev_frames.append(gray)
        if len(self.prev_frames) > self.frame_buffer_size:
            self.prev_frames.pop(0)
        
        if len(self.prev_frames) < 2:
            return False, 0.0
        
        # Calculate frame difference
        frame_delta = cv2.absdiff(self.prev_frames[-2], self.prev_frames[-1])
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Calculate movement amount
        movement = np.sum(thresh) / 255.0
        
        is_rapid = movement > self.rapid_movement_threshold * 1000
        
        return is_rapid, float(movement / 1000.0)
    
    def analyze_frame(self, frame):
        """Analyze a single frame for unusual activities"""
        activities = {
            "fall_detected": False,
            "rapid_movement": False,
            "fall_confidence": 0.0,
            "movement_speed": 0.0,
            "pose_detected": True  # Simplified - always true
        }
        
        # Detect rapid movement
        is_rapid, speed = self.detect_movement(frame)
        activities["rapid_movement"] = is_rapid
        activities["movement_speed"] = speed
        
        # Simplified fall detection based on movement patterns
        # In a real scenario, this would use pose estimation
        if speed > 50.0:  # Very high movement could indicate a fall
            activities["fall_detected"] = True
            activities["fall_confidence"] = min(speed / 100.0, 1.0)
        
        return activities, frame

detector = ActivityDetector()

@app.get("/")
async def root():
    return {"message": "Patient Monitoring System API", "status": "running"}

@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file for processing"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "message": "Video uploaded successfully"
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/process-video/{filename}")
async def process_video(filename: str):
    """Process uploaded video and detect activities"""
    try:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            return JSONResponse({
                "success": False,
                "error": "Video file not found"
            }, status_code=404)
        
        # Open video
        cap = cv2.VideoCapture(str(file_path))
        
        if not cap.isOpened():
            return JSONResponse({
                "success": False,
                "error": "Failed to open video"
            }, status_code=500)
        
        # Process video
        alerts = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every 5th frame for performance
            if frame_count % 5 == 0:
                activities, _ = detector.analyze_frame(frame)
                
                timestamp = frame_count / fps if fps > 0 else frame_count / 30.0
                
                # Generate alerts
                if activities["fall_detected"]:
                    alert = {
                        "type": "FALL",
                        "severity": "HIGH",
                        "timestamp": timestamp,
                        "frame": frame_count,
                        "confidence": activities["fall_confidence"],
                        "message": "Fall detected - Immediate attention required"
                    }
                    alerts.append(alert)
                    
                    # Send real-time alert via WebSocket
                    await broadcast_alert(alert)
                
                elif activities["rapid_movement"]:
                    alert = {
                        "type": "RAPID_MOVEMENT",
                        "severity": "MEDIUM",
                        "timestamp": timestamp,
                        "frame": frame_count,
                        "speed": activities["movement_speed"],
                        "message": "Rapid movement detected - Check patient"
                    }
                    alerts.append(alert)
                    
                    # Send real-time alert via WebSocket
                    await broadcast_alert(alert)
        
        cap.release()
        
        return JSONResponse({
            "success": True,
            "total_frames": total_frames,
            "processed_frames": frame_count,
            "alerts": alerts,
            "summary": {
                "fall_count": len([a for a in alerts if a["type"] == "FALL"]),
                "rapid_movement_count": len([a for a in alerts if a["type"] == "RAPID_MOVEMENT"])
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_alert(alert: dict):
    """Broadcast alert to all connected clients"""
    alert["timestamp_iso"] = datetime.now().isoformat()
    
    for connection in active_connections:
        try:
            await connection.send_json(alert)
        except:
            # Remove dead connections
            if connection in active_connections:
                active_connections.remove(connection)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
