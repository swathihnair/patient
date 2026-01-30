from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import mediapipe as mp
import numpy as np
import json
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class ActivityDetector:
    def __init__(self):
        self.prev_positions = []
        self.fall_threshold = 0.3  # Vertical position threshold
        self.rapid_movement_threshold = 0.15  # Movement speed threshold
        self.frame_buffer_size = 10
        
    def detect_fall(self, landmarks):
        """Detect fall based on pose landmarks"""
        if not landmarks:
            return False, 0.0
        
        # Get key points
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        # Calculate hip midpoint
        hip_y = (left_hip.y + right_hip.y) / 2
        
        # Fall detected if nose is close to hip level (person is horizontal)
        vertical_distance = abs(nose.y - hip_y)
        
        # Also check if person is low in frame
        is_fall = hip_y > 0.7 and vertical_distance < self.fall_threshold
        
        return is_fall, hip_y
    
    def detect_rapid_movement(self, landmarks):
        """Detect rapid movement based on position changes"""
        if not landmarks:
            return False, 0.0
        
        # Get center of mass (average of key points)
        key_points = [
            landmarks[mp_pose.PoseLandmark.NOSE.value],
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
            landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
        ]
        
        center_x = np.mean([p.x for p in key_points])
        center_y = np.mean([p.y for p in key_points])
        
        current_position = np.array([center_x, center_y])
        
        # Store position history
        self.prev_positions.append(current_position)
        if len(self.prev_positions) > self.frame_buffer_size:
            self.prev_positions.pop(0)
        
        # Calculate movement speed
        if len(self.prev_positions) >= 2:
            movement = np.linalg.norm(
                self.prev_positions[-1] - self.prev_positions[-2]
            )
            
            is_rapid = movement > self.rapid_movement_threshold
            return is_rapid, float(movement)
        
        return False, 0.0
    
    def analyze_frame(self, frame):
        """Analyze a single frame for unusual activities"""
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        activities = {
            "fall_detected": False,
            "rapid_movement": False,
            "fall_confidence": 0.0,
            "movement_speed": 0.0,
            "pose_detected": False
        }
        
        if results.pose_landmarks:
            activities["pose_detected"] = True
            landmarks = results.pose_landmarks.landmark
            
            # Detect fall
            is_fall, fall_conf = self.detect_fall(landmarks)
            activities["fall_detected"] = is_fall
            activities["fall_confidence"] = float(fall_conf)
            
            # Detect rapid movement
            is_rapid, speed = self.detect_rapid_movement(landmarks)
            activities["rapid_movement"] = is_rapid
            activities["movement_speed"] = speed
            
            # Draw pose landmarks on frame
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            )
        
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
                
                timestamp = frame_count / fps
                
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
