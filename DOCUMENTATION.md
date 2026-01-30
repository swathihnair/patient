# Patient Activity Monitoring System - Technical Documentation

## System Overview

This system provides real-time monitoring of patient activities using computer vision and pose estimation. It detects unusual activities such as falls and rapid movements, alerting healthcare staff through a web-based dashboard.

## Architecture

### High-Level Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  Video Source   │────────▶│  Backend Server  │◀───────▶│  Nurse Dashboard│
│  (Upload/CCTV)  │         │  (Python/FastAPI)│         │  (React)        │
│                 │         │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     │
                            ┌────────▼────────┐
                            │                 │
                            │   MediaPipe     │
                            │ Pose Detection  │
                            │                 │
                            └─────────────────┘
```

### Component Breakdown

#### 1. Backend (Python/FastAPI)

**File**: `backend/main.py`

**Key Components**:
- **FastAPI Application**: Handles HTTP requests and WebSocket connections
- **MediaPipe Integration**: Processes video frames for pose detection
- **ActivityDetector Class**: Implements detection algorithms
- **WebSocket Manager**: Broadcasts real-time alerts

**Detection Algorithms**:

1. **Fall Detection**
   - Tracks vertical position of body landmarks
   - Compares nose position to hip position
   - Triggers when hip is low and body is horizontal
   - Algorithm:
     ```python
     hip_y = (left_hip.y + right_hip.y) / 2
     vertical_distance = abs(nose.y - hip_y)
     is_fall = hip_y > 0.7 and vertical_distance < fall_threshold
     ```

2. **Rapid Movement Detection**
   - Calculates center of mass from key body points
   - Tracks position changes across frames
   - Detects sudden movements
   - Algorithm:
     ```python
     movement = ||current_position - previous_position||
     is_rapid = movement > rapid_movement_threshold
     ```

**API Endpoints**:
- `POST /api/upload-video`: Upload video file
- `POST /api/process-video/{filename}`: Process uploaded video
- `WS /ws/alerts`: WebSocket for real-time alerts
- `GET /api/health`: Health check

#### 2. Frontend (React)

**File**: `frontend/src/App.jsx`

**Key Features**:
- Real-time WebSocket connection for alerts
- Video upload with drag-and-drop
- Statistics dashboard
- Alert history with severity levels
- Audio notifications for critical events

**State Management**:
- `alerts`: Array of detected activities
- `stats`: Aggregated statistics
- `connectionStatus`: WebSocket connection state
- `uploadedFile`: Currently selected video file
- `isProcessing`: Processing state

#### 3. MediaPipe Pose Detection

**Landmarks Used**:
- Nose (0)
- Left/Right Shoulder (11, 12)
- Left/Right Hip (23, 24)
- Left/Right Knee (25, 26)
- Left/Right Ankle (27, 28)

**Configuration**:
```python
mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
```

## Data Flow

### Video Processing Flow

```
1. Video Upload
   ↓
2. Save to uploads/
   ↓
3. Open with OpenCV
   ↓
4. Extract frames (every 5th frame)
   ↓
5. Convert to RGB
   ↓
6. MediaPipe pose detection
   ↓
7. Analyze landmarks
   ↓
8. Detect activities
   ↓
9. Generate alerts
   ↓
10. Broadcast via WebSocket
    ↓
11. Display on dashboard
```

### Real-Time Alert Flow

```
Backend Detection → WebSocket Broadcast → Frontend Receives → Update UI → Audio Alert
```

## Configuration Parameters

### Backend Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fall_threshold` | 0.3 | Vertical distance threshold for fall detection |
| `rapid_movement_threshold` | 0.15 | Movement speed threshold |
| `frame_buffer_size` | 10 | Number of frames to analyze |
| `min_detection_confidence` | 0.5 | MediaPipe detection confidence |
| `min_tracking_confidence` | 0.5 | MediaPipe tracking confidence |

### Frontend Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `API_URL` | http://localhost:8000 | Backend API URL |
| `WS_URL` | ws://localhost:8000/ws/alerts | WebSocket URL |

## Alert Severity Levels

| Level | Trigger | Action |
|-------|---------|--------|
| HIGH | Fall detected | Immediate notification + audio alert |
| MEDIUM | Rapid movement | Visual notification |
| LOW | Normal activity | Log only |

## Performance Considerations

### Frame Processing
- Process every 5th frame for performance
- Reduces CPU usage by 80%
- Maintains detection accuracy

### Video Format Support
- MP4 (recommended)
- AVI
- MOV
- WebM

### Recommended Specifications

**Backend Server**:
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ for video storage

**Client Browser**:
- Modern browser with WebSocket support
- Chrome/Edge recommended
- Stable internet connection

## Future Enhancements

### Phase 1: CCTV Integration
- RTSP stream support
- Multi-camera monitoring
- Camera configuration interface

### Phase 2: Advanced Detection
- Custom TensorFlow models
- Activity classification
- Patient identification
- Abnormal behavior patterns

### Phase 3: Database Integration
- PostgreSQL for persistence
- Historical analytics
- Patient records
- Trend analysis

### Phase 4: Notifications
- SMS alerts via Twilio
- Email notifications
- Mobile app integration
- Escalation workflows

### Phase 5: Analytics
- Dashboard analytics
- Heat maps
- Activity reports
- Predictive analytics

## Security Considerations

### Current Implementation
- CORS enabled for development
- No authentication (demo mode)

### Production Requirements
- JWT authentication
- HTTPS/WSS encryption
- Role-based access control
- Video encryption at rest
- Audit logging
- HIPAA compliance measures

## Testing

### Manual Testing
1. Generate test video:
   ```bash
   cd backend
   python generate_test_video.py
   ```

2. Upload through dashboard
3. Verify alerts appear
4. Check WebSocket connection

### Test Scenarios
- Normal activity (no alerts)
- Rapid movement detection
- Fall detection
- Multiple activities in sequence

## Troubleshooting

### Common Issues

**1. WebSocket Connection Failed**
- Ensure backend is running
- Check firewall settings
- Verify port 8000 is available

**2. MediaPipe Installation Error**
- Update pip: `pip install --upgrade pip`
- Install with no cache: `pip install mediapipe --no-cache-dir`

**3. Video Processing Slow**
- Reduce video resolution
- Increase frame skip interval
- Use GPU acceleration (if available)

**4. No Pose Detected**
- Ensure person is visible in frame
- Check lighting conditions
- Verify camera angle

## Development Workflow

### Adding New Detection Algorithm

1. Create detection method in `ActivityDetector` class
2. Call method in `analyze_frame()`
3. Define alert structure
4. Update frontend alert display
5. Test with sample videos

### Example: Adding Seizure Detection

```python
def detect_seizure(self, landmarks):
    """Detect rapid repetitive movements"""
    # Implementation here
    return is_seizure, confidence

# In analyze_frame():
is_seizure, conf = self.detect_seizure(landmarks)
if is_seizure:
    activities["seizure_detected"] = True
    activities["seizure_confidence"] = conf
```

## API Reference

### REST Endpoints

#### Upload Video
```http
POST /api/upload-video
Content-Type: multipart/form-data

file: <video file>

Response:
{
  "success": true,
  "filename": "video.mp4",
  "message": "Video uploaded successfully"
}
```

#### Process Video
```http
POST /api/process-video/{filename}

Response:
{
  "success": true,
  "total_frames": 450,
  "processed_frames": 450,
  "alerts": [...],
  "summary": {
    "fall_count": 2,
    "rapid_movement_count": 5
  }
}
```

### WebSocket Protocol

#### Connect
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts');
```

#### Alert Message Format
```json
{
  "type": "FALL",
  "severity": "HIGH",
  "timestamp": 12.5,
  "frame": 375,
  "confidence": 0.85,
  "message": "Fall detected - Immediate attention required",
  "timestamp_iso": "2026-01-30T23:15:30.123Z"
}
```

## Deployment

### Docker Deployment (Future)

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Production Checklist
- [ ] Enable HTTPS/WSS
- [ ] Add authentication
- [ ] Configure database
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Enable logging
- [ ] Set up alerts
- [ ] Load testing
- [ ] Security audit

## License & Credits

**Built with**:
- MediaPipe (Apache 2.0)
- FastAPI (MIT)
- React (MIT)
- OpenCV (Apache 2.0)

**Created for**: Healthcare Innovation Hackathon 2026

---

For questions or contributions, please refer to the main README.md
