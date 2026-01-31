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
from google import genai
from PIL import Image
import io
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Patient Monitoring System")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MediaPipe setup - New Tasks API
try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    import mediapipe as mp
    
    # Download pose landmarker model if not exists
    import urllib.request
    model_path = "pose_landmarker.task"
    if not os.path.exists(model_path):
        print("Downloading pose landmarker model...")
        url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
        urllib.request.urlretrieve(url, model_path)
        print("Model downloaded successfully")
    
    # Create pose landmarker
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=False,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    pose_detector = vision.PoseLandmarker.create_from_options(options)
    
    # Pose landmark indices (same as old MediaPipe)
    class PoseLandmark:
        NOSE = 0
        LEFT_SHOULDER = 11
        RIGHT_SHOULDER = 12
        LEFT_HIP = 23
        RIGHT_HIP = 24
    
    mp_pose_landmark = PoseLandmark
    print("MediaPipe pose detection initialized successfully")
except Exception as e:
    print(f"Warning: MediaPipe pose detection not available: {e}")
    pose_detector = None
    mp_pose_landmark = None

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY loaded: {'Yes' if GEMINI_API_KEY else 'No'}")
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("Gemini client initialized successfully")
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        client = None
else:
    print("Warning: GEMINI_API_KEY not found in environment")
    client = None

class ActivityDetector:
    def __init__(self):
        self.prev_positions = []
        self.prev_landmarks_history = []  # For seizure detection
        self.bed_region = None  # Will be set based on first detection
        self.breathing_history = []  # For breathing rate
        self.fall_threshold = 0.3  # Vertical position threshold
        self.rapid_movement_threshold = 0.08  # Movement speed threshold (lowered from 0.15)
        self.frame_buffer_size = 10
        self.seizure_buffer_size = 30  # Frames to analyze for seizure
        self.breathing_buffer_size = 60  # Frames for breathing (2 seconds at 30fps)
    
    def reset(self):
        """Reset detector state for new video"""
        self.prev_positions = []
        self.prev_landmarks_history = []
        self.bed_region = None
        self.breathing_history = []
        print("Detector state reset for new video")
        
    def detect_fall(self, landmarks):
        """Detect fall based on pose landmarks"""
        if not landmarks:
            return False, 0.0
        
        # Get key points
        nose = landmarks[mp_pose_landmark.NOSE]
        left_hip = landmarks[mp_pose_landmark.LEFT_HIP]
        right_hip = landmarks[mp_pose_landmark.RIGHT_HIP]
        
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
            landmarks[mp_pose_landmark.NOSE],
            landmarks[mp_pose_landmark.LEFT_SHOULDER],
            landmarks[mp_pose_landmark.RIGHT_SHOULDER],
            landmarks[mp_pose_landmark.LEFT_HIP],
            landmarks[mp_pose_landmark.RIGHT_HIP],
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
    
    def detect_seizure(self, landmarks):
        """Detect seizure-like convulsive movements"""
        if not landmarks:
            return False, 0.0
        
        # Track multiple body parts for erratic movement
        key_points = [
            landmarks[mp_pose_landmark.LEFT_SHOULDER],
            landmarks[mp_pose_landmark.RIGHT_SHOULDER],
            landmarks[mp_pose_landmark.LEFT_HIP],
            landmarks[mp_pose_landmark.RIGHT_HIP],
        ]
        
        # Calculate variance in positions
        positions = np.array([[p.x, p.y] for p in key_points])
        
        # Store landmark history
        self.prev_landmarks_history.append(positions)
        if len(self.prev_landmarks_history) > self.seizure_buffer_size:
            self.prev_landmarks_history.pop(0)
        
        # Need enough history to detect seizure
        if len(self.prev_landmarks_history) < 20:
            return False, 0.0
        
        # Calculate movement variance across frames
        movements = []
        for i in range(1, len(self.prev_landmarks_history)):
            diff = np.linalg.norm(
                self.prev_landmarks_history[i] - self.prev_landmarks_history[i-1]
            )
            movements.append(diff)
        
        # High variance + high frequency = seizure
        movement_variance = np.var(movements)
        movement_mean = np.mean(movements)
        
        # Seizure: high variance with consistent high movement
        is_seizure = movement_variance > 0.01 and movement_mean > 0.05
        
        return is_seizure, float(movement_variance)
    
    def detect_bed_exit(self, landmarks, frame_shape):
        """Detect when patient exits bed area"""
        if not landmarks:
            return False, 0.0
        
        # Get hip position (center of body)
        left_hip = landmarks[mp_pose_landmark.LEFT_HIP]
        right_hip = landmarks[mp_pose_landmark.RIGHT_HIP]
        
        hip_x = (left_hip.x + right_hip.x) / 2
        hip_y = (left_hip.y + right_hip.y) / 2
        
        # Initialize bed region on first detection (assume patient starts in bed)
        if self.bed_region is None:
            self.bed_region = {
                'x_min': hip_x - 0.2,
                'x_max': hip_x + 0.2,
                'y_min': hip_y - 0.2,
                'y_max': hip_y + 0.2
            }
            return False, 0.0
        
        # Check if patient is outside bed region
        is_outside = (
            hip_x < self.bed_region['x_min'] or 
            hip_x > self.bed_region['x_max'] or
            hip_y < self.bed_region['y_min'] or 
            hip_y > self.bed_region['y_max']
        )
        
        # Calculate distance from bed center
        bed_center_x = (self.bed_region['x_min'] + self.bed_region['x_max']) / 2
        bed_center_y = (self.bed_region['y_min'] + self.bed_region['y_max']) / 2
        distance = np.sqrt((hip_x - bed_center_x)**2 + (hip_y - bed_center_y)**2)
        
        return is_outside, float(distance)
    
    def detect_abnormal_posture(self, landmarks):
        """Detect unusual body positions"""
        if not landmarks:
            return False, 0.0, "None"
        
        nose = landmarks[mp_pose_landmark.NOSE]
        left_shoulder = landmarks[mp_pose_landmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose_landmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp_pose_landmark.LEFT_HIP]
        right_hip = landmarks[mp_pose_landmark.RIGHT_HIP]
        
        # Calculate body angles
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_y = (left_hip.y + right_hip.y) / 2
        
        # Check for various abnormal postures
        posture_type = "Normal"
        is_abnormal = False
        confidence = 0.0
        
        # 1. Upside down (head below hips)
        if nose.y > hip_y + 0.1:
            is_abnormal = True
            posture_type = "Upside Down"
            confidence = abs(nose.y - hip_y)
        
        # 2. Extreme lean (shoulders very tilted)
        shoulder_tilt = abs(left_shoulder.y - right_shoulder.y)
        if shoulder_tilt > 0.15:
            is_abnormal = True
            posture_type = "Extreme Lean"
            confidence = shoulder_tilt
        
        # 3. Twisted body (shoulders and hips misaligned)
        shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
        hip_center_x = (left_hip.x + right_hip.x) / 2
        body_twist = abs(shoulder_center_x - hip_center_x)
        if body_twist > 0.2:
            is_abnormal = True
            posture_type = "Twisted Body"
            confidence = body_twist
        
        # 4. Curled up (very compressed vertically)
        body_height = abs(nose.y - hip_y)
        if body_height < 0.15:
            is_abnormal = True
            posture_type = "Curled Up"
            confidence = 1.0 - body_height
        
        return is_abnormal, float(confidence), posture_type
    
    def detect_breathing_rate(self, landmarks):
        """Estimate breathing rate from chest movement"""
        if not landmarks:
            return 0.0, "Unknown"
        
        # Track shoulder movement (rises with breathing)
        left_shoulder = landmarks[mp_pose_landmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose_landmark.RIGHT_SHOULDER]
        
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        
        # Store breathing history
        self.breathing_history.append(shoulder_y)
        if len(self.breathing_history) > self.breathing_buffer_size:
            self.breathing_history.pop(0)
        
        # Need enough data to estimate breathing
        if len(self.breathing_history) < 30:
            return 0.0, "Calculating..."
        
        # Count peaks (breaths) in the signal
        breathing_array = np.array(self.breathing_history)
        
        # Simple peak detection
        peaks = 0
        for i in range(1, len(breathing_array) - 1):
            if breathing_array[i] > breathing_array[i-1] and breathing_array[i] > breathing_array[i+1]:
                # Check if peak is significant
                if abs(breathing_array[i] - np.mean(breathing_array)) > 0.005:
                    peaks += 1
        
        # Convert to breaths per minute (assuming 30 fps, 60 frames = 2 seconds)
        breaths_per_minute = (peaks / len(self.breathing_history)) * 30 * 60
        
        # Classify breathing rate
        if breaths_per_minute < 12:
            status = "Slow (Bradypnea)"
        elif breaths_per_minute > 20:
            status = "Fast (Tachypnea)"
        else:
            status = "Normal"
        
        return float(breaths_per_minute), status
        
        return False, 0.0
    
    def analyze_frame(self, frame):
        """Analyze a single frame for unusual activities"""
        if pose_detector is None:
            # MediaPipe not available
            return {
                "fall_detected": False,
                "rapid_movement": False,
                "seizure_detected": False,
                "bed_exit_detected": False,
                "abnormal_posture_detected": False,
                "fall_confidence": 0.0,
                "movement_speed": 0.0,
                "breathing_rate": 0.0,
                "breathing_status": "Unknown",
                "posture_type": "Unknown",
                "pose_detected": False
            }, frame
            
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect pose
        detection_result = pose_detector.detect(mp_image)
        
        activities = {
            "fall_detected": False,
            "rapid_movement": False,
            "seizure_detected": False,
            "bed_exit_detected": False,
            "abnormal_posture_detected": False,
            "fall_confidence": 0.0,
            "movement_speed": 0.0,
            "seizure_confidence": 0.0,
            "bed_exit_distance": 0.0,
            "posture_confidence": 0.0,
            "posture_type": "Normal",
            "breathing_rate": 0.0,
            "breathing_status": "Unknown",
            "pose_detected": False
        }
        
        if detection_result.pose_landmarks:
            activities["pose_detected"] = True
            landmarks = detection_result.pose_landmarks[0]  # Get first person
            
            # 1. Detect fall
            is_fall, fall_conf = self.detect_fall(landmarks)
            activities["fall_detected"] = is_fall
            activities["fall_confidence"] = float(fall_conf)
            
            # 2. Detect rapid movement
            is_rapid, speed = self.detect_rapid_movement(landmarks)
            activities["rapid_movement"] = is_rapid
            activities["movement_speed"] = speed
            
            # 3. Detect seizure
            is_seizure, seizure_conf = self.detect_seizure(landmarks)
            activities["seizure_detected"] = is_seizure
            activities["seizure_confidence"] = seizure_conf
            
            # 4. Detect bed exit
            is_bed_exit, exit_distance = self.detect_bed_exit(landmarks, frame.shape)
            activities["bed_exit_detected"] = is_bed_exit
            activities["bed_exit_distance"] = exit_distance
            
            # 5. Detect abnormal posture
            is_abnormal, posture_conf, posture_type = self.detect_abnormal_posture(landmarks)
            activities["abnormal_posture_detected"] = is_abnormal
            activities["posture_confidence"] = posture_conf
            activities["posture_type"] = posture_type
            
            # 6. Detect breathing rate
            breathing_rate, breathing_status = self.detect_breathing_rate(landmarks)
            activities["breathing_rate"] = breathing_rate
            activities["breathing_status"] = breathing_status
            
            # Draw pose landmarks on frame (simple circles)
            for landmark in landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            
            # Draw alerts on frame
            y_offset = 30
            if is_fall:
                cv2.putText(frame, "FALL DETECTED!", (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                y_offset += 40
            if is_seizure:
                cv2.putText(frame, "SEIZURE DETECTED!", (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                y_offset += 40
            if is_bed_exit:
                cv2.putText(frame, "BED EXIT DETECTED!", (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 0), 2)
                y_offset += 40
            if is_abnormal:
                cv2.putText(frame, f"ABNORMAL POSTURE: {posture_type}", (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                y_offset += 40
            
            # Display breathing rate
            cv2.putText(frame, f"Breathing: {breathing_rate:.1f} bpm ({breathing_status})", 
                       (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
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
        
        # Reset detector state for new video
        detector.reset()
        print(f"Processing video: {filename}, Total frames: {total_frames}, FPS: {fps}")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every 5th frame for performance
            if frame_count % 5 == 0:
                activities, _ = detector.analyze_frame(frame)
                
                timestamp = frame_count / fps
                
                # Debug logging
                if activities["pose_detected"]:
                    print(f"Frame {frame_count}: Pose detected, Movement speed: {activities['movement_speed']:.4f}")
                
                # Generate alerts for all detection types
                if activities["fall_detected"]:
                    alert = {
                        "type": "FALL",
                        "severity": "CRITICAL",
                        "timestamp": timestamp,
                        "frame": frame_count,
                        "confidence": activities["fall_confidence"],
                        "message": "🚨 Fall detected - Immediate attention required!"
                    }
                    alerts.append(alert)
                    await broadcast_alert(alert)
                    print(f"ALERT: Fall detected at frame {frame_count}")
                
                if activities["seizure_detected"]:
                    alert = {
                        "type": "SEIZURE",
                        "severity": "CRITICAL",
                        "timestamp": timestamp,
                        "frame": frame_count,
                        "confidence": activities["seizure_confidence"],
                        "message": "🚨 Seizure detected - Emergency response needed!"
                    }
                    alerts.append(alert)
                    await broadcast_alert(alert)
                    print(f"ALERT: Seizure detected at frame {frame_count}")
                
                if activities["bed_exit_detected"]:
                    alert = {
                        "type": "BED_EXIT",
                        "severity": "HIGH",
                        "timestamp": timestamp,
                        "frame": frame_count,
                        "distance": activities["bed_exit_distance"],
                        "message": "⚠️ Patient left bed - Check immediately!"
                    }
                    alerts.append(alert)
                    await broadcast_alert(alert)
                    print(f"ALERT: Bed exit detected at frame {frame_count}")
                
                if activities["abnormal_posture_detected"]:
                    alert = {
                        "type": "ABNORMAL_POSTURE",
                        "severity": "MEDIUM",
                        "timestamp": timestamp,
                        "frame": frame_count,
                        "posture_type": activities["posture_type"],
                        "confidence": activities["posture_confidence"],
                        "message": f"⚠️ Abnormal posture detected: {activities['posture_type']}"
                    }
                    alerts.append(alert)
                    await broadcast_alert(alert)
                    print(f"ALERT: Abnormal posture detected at frame {frame_count}: {activities['posture_type']}")
                
                if activities["rapid_movement"]:
                    alert = {
                        "type": "RAPID_MOVEMENT",
                        "severity": "MEDIUM",
                        "timestamp": timestamp,
                        "frame": frame_count,
                        "speed": activities["movement_speed"],
                        "message": "⚡ Rapid movement detected - Check patient"
                    }
                    alerts.append(alert)
                    await broadcast_alert(alert)
                    print(f"ALERT: Rapid movement detected at frame {frame_count}, speed: {activities['movement_speed']:.4f}")
                
                # Monitor breathing rate (alert if abnormal)
                if activities["breathing_rate"] > 0:
                    if activities["breathing_rate"] < 10 or activities["breathing_rate"] > 25:
                        alert = {
                            "type": "ABNORMAL_BREATHING",
                            "severity": "HIGH",
                            "timestamp": timestamp,
                            "frame": frame_count,
                            "breathing_rate": activities["breathing_rate"],
                            "status": activities["breathing_status"],
                            "message": f"⚠️ Abnormal breathing: {activities['breathing_rate']:.1f} bpm ({activities['breathing_status']})"
                        }
                        alerts.append(alert)
                        await broadcast_alert(alert)
        
        cap.release()
        
        print(f"Video processing complete: {len(alerts)} total alerts")
        print(f"  - Falls: {len([a for a in alerts if a['type'] == 'FALL'])}")
        print(f"  - Rapid movements: {len([a for a in alerts if a['type'] == 'RAPID_MOVEMENT'])}")
        print(f"  - Seizures: {len([a for a in alerts if a['type'] == 'SEIZURE'])}")
        print(f"  - Bed exits: {len([a for a in alerts if a['type'] == 'BED_EXIT'])}")
        print(f"  - Abnormal postures: {len([a for a in alerts if a['type'] == 'ABNORMAL_POSTURE'])}")
        print(f"  - Breathing alerts: {len([a for a in alerts if a['type'] == 'ABNORMAL_BREATHING'])}")
        
        return JSONResponse({
            "success": True,
            "total_frames": total_frames,
            "processed_frames": frame_count,
            "alerts": alerts,
            "summary": {
                "fall_count": len([a for a in alerts if a["type"] == "FALL"]),
                "seizure_count": len([a for a in alerts if a["type"] == "SEIZURE"]),
                "bed_exit_count": len([a for a in alerts if a["type"] == "BED_EXIT"]),
                "abnormal_posture_count": len([a for a in alerts if a["type"] == "ABNORMAL_POSTURE"]),
                "rapid_movement_count": len([a for a in alerts if a["type"] == "RAPID_MOVEMENT"]),
                "abnormal_breathing_count": len([a for a in alerts if a["type"] == "ABNORMAL_BREATHING"])
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

@app.post("/api/compare-ward-images")
async def compare_ward_images(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...)
):
    """Compare two ward images to detect missing patients using Gemini AI"""
    try:
        if not client:
            return JSONResponse({
                "success": False,
                "error": "GEMINI_API_KEY not configured. Please set it in your .env file."
            }, status_code=500)
        
        print("Reading images...")
        # Read both images
        image1_data = await image1.read()
        image2_data = await image2.read()
        pil_image1 = Image.open(io.BytesIO(image1_data))
        pil_image2 = Image.open(io.BytesIO(image2_data))
        print(f"Images loaded: {pil_image1.size}, {pil_image2.size}")
        
        # Create prompt for Gemini
        prompt = """Compare these two hospital ward images and identify any missing patients.

Image 1 (Before): Reference image with all patients present
Image 2 (After): Current ward state to check

Please analyze and provide a detailed comparison in the following JSON format:
{
    "summary": "Brief overview of what changed between the two images",
    "total_missing": number of patients missing,
    "missing_patients": [
        {
            "bed_number": "Bed identifier (e.g., 'Bed 1', 'Bed 3 - Left side')",
            "description": "Description of the missing patient's location and what you observe"
        }
    ]
}

Focus on:
1. Identifying beds/locations that had patients in Image 1 but are empty in Image 2
2. Noting specific bed positions (left, right, center, near window, etc.)
3. Describing the exact location to help staff quickly identify missing patients
4. Being precise about which patients are no longer present

If all patients are present in both images, set total_missing to 0 and missing_patients to an empty array."""

        print("Calling Gemini API...")
        # Call Gemini API with new SDK
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, pil_image1, pil_image2]
        )
        print("Gemini API response received")
        
        # Parse response
        response_text = response.text.strip()
        print(f"Response text: {response_text[:200]}...")
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        try:
            comparison_result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            # If JSON parsing fails, create a structured response from text
            comparison_result = {
                "summary": response_text[:200],
                "total_missing": 0,
                "missing_patients": [],
                "raw_response": response_text
            }
        
        return JSONResponse({
            "success": True,
            "comparison_result": comparison_result
        })
        
    except Exception as e:
        print(f"Error in compare_ward_images: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/analyze-ward-presence")
async def analyze_ward_presence(
    image: UploadFile = File(...),
    expected_beds: int = 10
):
    """Analyze ward image to detect patient presence at each bed using Gemini AI"""
    try:
        if not client:
            return JSONResponse({
                "success": False,
                "error": "GEMINI_API_KEY not configured. Please set it in your .env file."
            }, status_code=500)
        
        # Read image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Create prompt for Gemini
        prompt = f"""Analyze this hospital ward image and identify patient presence at each bed location.

Expected number of beds: {expected_beds}

Please provide a detailed analysis in the following JSON format:
{{
    "summary": "Brief overview of the ward status",
    "total_beds": number of beds visible in the image,
    "occupied_beds": number of beds with patients present,
    "empty_beds": number of empty beds,
    "empty_spots": [
        {{
            "location": "Bed position (e.g., 'Bed 1 - Left side', 'Bed 3 - Center')",
            "description": "Description of the empty bed location"
        }}
    ]
}}

Focus on:
1. Identifying all bed locations in the ward
2. Detecting human presence at each bed
3. Noting which specific beds/spots are empty
4. Providing clear location descriptions for empty beds

Be specific about bed positions (left, right, center, near window, etc.) to help staff locate empty beds quickly."""

        # Call Gemini API with new SDK
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, pil_image]
        )
        
        # Parse response
        response_text = response.text.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, create a structured response from text
            analysis = {
                "summary": response_text[:200],
                "total_beds": expected_beds,
                "occupied_beds": 0,
                "empty_beds": 0,
                "empty_spots": [],
                "raw_response": response_text
            }
        
        return JSONResponse({
            "success": True,
            "analysis": analysis
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
