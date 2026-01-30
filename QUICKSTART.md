# 🚀 Quick Start Guide - Patient Monitoring System

## ⚡ Fastest Way to Get Started

### Option 1: Automated Start (Recommended)

Simply run the startup script:

```powershell
.\start.ps1
```

This will:
- ✅ Check Python and Node.js installations
- ✅ Create virtual environment (if needed)
- ✅ Install all dependencies
- ✅ Start both backend and frontend servers
- ✅ Open in separate terminal windows

### Option 2: Manual Start

#### Step 1: Backend Setup (Terminal 1)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

✅ Backend running at: http://localhost:8000

#### Step 2: Frontend Setup (Terminal 2)

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:5173

## 🎬 Testing the System

### Generate Test Video

```powershell
cd backend
python generate_test_video.py
```

This creates `uploads/test_patient.mp4` with simulated activities.

### Use the Dashboard

1. Open http://localhost:5173 in your browser
2. Drag and drop the test video (or any patient video)
3. Click "Analyze Video"
4. Watch alerts appear in real-time!

## 📊 What You'll See

### Dashboard Features
- **Statistics Cards**: Total alerts, falls, rapid movements
- **Upload Section**: Drag & drop video files
- **Alert Feed**: Real-time activity notifications
- **Connection Status**: WebSocket connection indicator

### Alert Types
- 🚨 **FALL** (High Severity): Red alert with audio notification
- ⚡ **RAPID_MOVEMENT** (Medium Severity): Yellow alert

## 🎯 Next Steps

1. **Try Different Videos**: Upload your own test videos
2. **Adjust Sensitivity**: Modify thresholds in `backend/main.py`
3. **Customize UI**: Edit `frontend/src/index.css` for styling
4. **Add Features**: Extend detection algorithms

## 📚 Documentation

- **README.md**: Project overview and features
- **DOCUMENTATION.md**: Technical architecture and API reference
- **backend/README.md**: Backend-specific guide
- **frontend/README.md**: Frontend-specific guide

## 🔧 Troubleshooting

### Backend won't start
```powershell
# Check Python version (need 3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```powershell
# Check Node version (need 16+)
node --version

# Clear cache and reinstall
rm -r node_modules
npm install
```

### WebSocket connection failed
- Ensure backend is running first
- Check if port 8000 is available
- Verify no firewall blocking

## 🎨 Customization

### Change Detection Sensitivity

Edit `backend/main.py`:
```python
fall_threshold = 0.3  # Lower = more sensitive
rapid_movement_threshold = 0.15  # Lower = more sensitive
```

### Change UI Colors

Edit `frontend/src/index.css`:
```css
--primary-hue: 200;  /* Blue theme */
--accent-hue: 340;   /* Pink accent */
```

## 🌟 Features Overview

✅ Real-time pose detection with MediaPipe  
✅ Fall detection algorithm  
✅ Rapid movement detection  
✅ WebSocket real-time alerts  
✅ Beautiful dark-themed dashboard  
✅ Video upload with drag & drop  
✅ Audio alerts for critical events  
✅ Statistics and analytics  
✅ Responsive design  
✅ Future-ready for CCTV integration  

## 📞 Need Help?

- Check the full **README.md** for detailed information
- Review **DOCUMENTATION.md** for technical details
- Check the API docs at http://localhost:8000/docs

---

**Ready to monitor patients? Let's go! 🏥**
