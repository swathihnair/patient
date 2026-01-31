# How to Start the Patient Monitoring System

## Quick Start (Both Backend & Frontend)

### Option 1: Use the PowerShell Script (Easiest)
```powershell
.\start.ps1
```

### Option 2: Manual Start

#### Step 1: Start Backend (Terminal 1)
```bash
cd backend
python main.py
```
You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
MediaPipe pose detection initialized successfully
```

#### Step 2: Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5175/
➜  Network: use --host to expose
```

#### Step 3: Open Browser
Navigate to: `http://localhost:5175`

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'mediapipe'`
**Solution**: 
```bash
cd backend
pip install -r requirements.txt
```

**Problem**: Backend won't start
**Solution**: Check if port 8000 is already in use
```bash
# Windows
netstat -ano | findstr :8000
```

### Frontend Issues

**Problem**: `npm: command not found`
**Solution**: Install Node.js from https://nodejs.org/

**Problem**: `Cannot find module`
**Solution**: Install dependencies
```bash
cd frontend
npm install
```

**Problem**: Port 5175 already in use
**Solution**: Kill the process or use a different port
```bash
# The dev server will automatically try 5176, 5177, etc.
```

---

## Verify Everything is Working

### 1. Check Backend Health
Open browser: `http://localhost:8000/api/health`

Should see:
```json
{
  "status": "healthy",
  "active_connections": 0,
  "timestamp": "2026-01-31T..."
}
```

### 2. Check Frontend
Open browser: `http://localhost:5175`

Should see:
- Patient Monitor dashboard
- 7 stat cards (Total Alerts, Fall Incidents, Seizure Alerts, etc.)
- Room cards
- Upload section

### 3. Check WebSocket Connection
In the frontend, look at the top-right corner:
- Should show green dot with "Connected"

---

## What's Working Now

All features are working:
- ✅ Fall detection (original)
- ✅ Rapid movement detection (original)
- ✅ Seizure detection (NEW)
- ✅ Bed exit detection (NEW)
- ✅ Abnormal posture detection (NEW)
- ✅ Breathing rate monitoring (NEW)
- ✅ General ward image comparison (Gemini AI)
- ✅ Patient details from Google Sheets

---

## Testing the System

1. **Upload a test video**:
   - Click "Choose File" or drag-drop a video
   - Click "Analyze Video"
   - Wait for processing
   - See alerts appear in real-time

2. **Check General Ward**:
   - Select "General Ward" from dropdown
   - Upload two ward images (before/after)
   - Click "Compare Images"
   - See missing patient analysis

---

## Common Issues After Updates

### "I lost the previous working models"

**What actually happened**: 
- The code is still there (fall and rapid movement detection)
- The frontend dev server just needs to be restarted
- No code was removed, only new features were added

**Solution**: 
- Restart the frontend: `cd frontend && npm run dev`
- The backend is already running (you can see it's healthy)

### "Alerts not showing"

**Check**:
1. Backend running? → `http://localhost:8000/api/health`
2. Frontend running? → `http://localhost:5175`
3. WebSocket connected? → Look for green dot in UI
4. Video has clear patient view? → MediaPipe needs to see the person

---

## System Architecture

```
┌─────────────────┐
│   Frontend      │  Port 5175
│   (React/Vite)  │  
└────────┬────────┘
         │
         │ HTTP + WebSocket
         │
┌────────▼────────┐
│   Backend       │  Port 8000
│   (FastAPI)     │
└────────┬────────┘
         │
         ├─► MediaPipe (Pose Detection)
         ├─► Google Gemini AI (Image Comparison)
         └─► Google Sheets API (Patient Details)
```

---

## Next Steps

1. Start both servers (backend + frontend)
2. Open `http://localhost:5175` in browser
3. Upload a test video
4. Watch the magic happen! 🎉

All your previous working models are still there - nothing was lost!
