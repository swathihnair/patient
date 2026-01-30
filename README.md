# Patient Activity Monitoring System 🏥

A real-time patient monitoring system that detects unusual activities like falls and rapid movements using MediaPipe pose detection and computer vision. Built for healthcare professionals to monitor patients through video feeds.

## 🌟 Features

- **Fall Detection**: Automatically detects when a patient falls using pose estimation
- **Rapid Movement Detection**: Identifies sudden or unusual movements
- **Real-time Alerts**: WebSocket-based instant notifications to nurse dashboard
- **Video Upload**: Support for video file uploads (hackathon demo mode)
- **Future-Ready**: Architecture designed for CCTV integration
- **Beautiful Dashboard**: Modern, responsive React interface with dark theme
- **Activity Statistics**: Real-time metrics and alert history

## 🏗️ Architecture

### Backend (Python)
- **FastAPI**: High-performance async web framework
- **MediaPipe**: Google's pose detection library for human pose estimation
- **OpenCV**: Video processing and frame analysis
- **WebSocket**: Real-time bidirectional communication
- **TensorFlow**: Ready for custom vision model integration

### Frontend (React)
- **React + Vite**: Fast, modern development experience
- **WebSocket Client**: Real-time alert reception
- **Drag & Drop**: Intuitive video upload interface
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **npm or yarn**

## 🚀 Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the backend server:
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

## 📖 Usage

### For Hackathon Demo (Video Upload)

1. Open the dashboard at `http://localhost:5173`
2. Drag and drop a video file or click "Choose File"
3. Click "Analyze Video" to process
4. Watch real-time alerts appear on the dashboard
5. View statistics and alert history

### For Production (CCTV Integration)

The system is designed to be extended for CCTV integration. Future implementation will include:

1. **RTSP Stream Support**: Connect to IP cameras
2. **Multi-Camera Monitoring**: Monitor multiple patients simultaneously
3. **Continuous Processing**: 24/7 real-time monitoring
4. **Alert Persistence**: Database storage for alert history
5. **User Authentication**: Secure access control

## 🎯 Detection Algorithms

### Fall Detection
- Uses MediaPipe pose landmarks to track body position
- Detects when patient's hip position drops significantly
- Analyzes vertical distance between nose and hip
- Triggers HIGH severity alert

### Rapid Movement Detection
- Tracks center of mass movement across frames
- Calculates movement speed using position history
- Detects sudden movements that may indicate distress
- Triggers MEDIUM severity alert

## 🔧 Configuration

### Backend Configuration (main.py)

```python
# Adjust detection sensitivity
fall_threshold = 0.3  # Lower = more sensitive
rapid_movement_threshold = 0.15  # Lower = more sensitive
frame_buffer_size = 10  # Frames to analyze for movement
```

### Frontend Configuration (App.jsx)

```javascript
const API_URL = 'http://localhost:8000';  // Backend URL
```

## 📊 API Endpoints

### REST API

- `GET /` - Health check
- `POST /api/upload-video` - Upload video file
- `POST /api/process-video/{filename}` - Process uploaded video
- `GET /api/health` - System health status

### WebSocket

- `WS /ws/alerts` - Real-time alert stream

## 🎨 Dashboard Features

- **Live Connection Status**: Shows WebSocket connection state
- **Statistics Cards**: Total alerts, falls, rapid movements
- **Drag & Drop Upload**: Easy video file upload
- **Real-time Alerts**: Instant notifications with severity levels
- **Alert History**: Complete log of all detected activities
- **Audio Alerts**: Sound notification for high-severity events

## 🔮 Future Enhancements

1. **CCTV Integration**
   - RTSP stream support
   - Multi-camera dashboard
   - Camera management interface

2. **Advanced Detection**
   - Custom vision models for specific activities
   - Patient identification
   - Abnormal behavior patterns
   - Seizure detection

3. **Database Integration**
   - PostgreSQL for alert persistence
   - Patient records
   - Historical analytics

4. **Notifications**
   - SMS alerts
   - Email notifications
   - Mobile app push notifications

5. **Analytics Dashboard**
   - Trend analysis
   - Patient activity reports
   - Heat maps and visualizations

## 🛠️ Technology Stack

### Backend
- FastAPI 0.109.0
- MediaPipe 0.10.9
- OpenCV 4.9.0
- TensorFlow 2.15.0
- WebSockets 12.0

### Frontend
- React 18
- Vite 5
- Native WebSocket API
- Modern CSS with CSS Variables

## 📝 Project Structure

```
patient-monitoring/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── uploads/            # Uploaded video storage
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   └── index.css       # Styling
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
│
└── README.md
```

## 🐛 Troubleshooting

### Backend Issues

**MediaPipe Installation Error**
```bash
pip install --upgrade pip
pip install mediapipe --no-cache-dir
```

**Port Already in Use**
- Change port in `main.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`

### Frontend Issues

**WebSocket Connection Failed**
- Ensure backend is running on port 8000
- Check CORS settings in backend

**Video Upload Failed**
- Check file format (MP4, AVI, MOV supported)
- Ensure backend uploads directory exists

## 📄 License

This project is created for hackathon purposes. Feel free to use and modify.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgments

- MediaPipe by Google for pose detection
- FastAPI for the excellent web framework
- React team for the amazing frontend library

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Built with ❤️ for better patient care**
