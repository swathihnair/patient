# How to Restart the Backend

## Why Restart?
The backend code has been updated with:
- ✅ Lower rapid movement threshold (0.08 instead of 0.15) - more sensitive
- ✅ Debug logging to see what's being detected
- ✅ Detector state reset for each new video
- ✅ Summary output after processing

## Quick Restart

### Step 1: Stop the Current Backend
Find the Python process and stop it:

**Windows (PowerShell):**
```powershell
# Find the process
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Stop it (replace PID with actual process ID)
Stop-Process -Id <PID>
```

Or simply press `Ctrl+C` in the terminal where backend is running.

### Step 2: Start Backend Again
```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
MediaPipe pose detection initialized successfully
GEMINI_API_KEY loaded: Yes
Gemini client initialized successfully
```

## What Changed

### 1. Lower Threshold
**Before:** `rapid_movement_threshold = 0.15`
**After:** `rapid_movement_threshold = 0.08`

This makes the system more sensitive to movement. Even smaller movements will now trigger alerts.

### 2. Debug Logging
Now you'll see in the backend terminal:
```
Frame 5: Pose detected, Movement speed: 0.0234
Frame 10: Pose detected, Movement speed: 0.0456
ALERT: Rapid movement detected at frame 15, speed: 0.0912
```

This helps you understand what's being detected.

### 3. State Reset
Each video now starts fresh:
```
Detector state reset for new video
Processing video: demo_video.mp4, Total frames: 450, FPS: 30.0
```

### 4. Summary Output
After processing:
```
Video processing complete: 12 total alerts
  - Falls: 0
  - Rapid movements: 8
  - Seizures: 0
  - Bed exits: 2
  - Abnormal postures: 2
  - Breathing alerts: 0
```

## Testing After Restart

1. **Restart backend** (see above)
2. **Keep frontend running** (no need to restart)
3. **Upload your rapid movement video again**
4. **Watch the backend terminal** for debug output
5. **Check frontend** for alerts

## Expected Output

### Backend Terminal
```
Processing video: rapid_movement.mp4, Total frames: 300, FPS: 30.0
Detector state reset for new video
Frame 5: Pose detected, Movement speed: 0.0123
Frame 10: Pose detected, Movement speed: 0.0234
Frame 15: Pose detected, Movement speed: 0.0456
Frame 20: Pose detected, Movement speed: 0.0912
ALERT: Rapid movement detected at frame 20, speed: 0.0912
Frame 25: Pose detected, Movement speed: 0.1234
ALERT: Rapid movement detected at frame 25, speed: 0.1234
...
Video processing complete: 15 total alerts
  - Falls: 0
  - Rapid movements: 15
  - Seizures: 0
  - Bed exits: 0
  - Abnormal postures: 0
  - Breathing alerts: 0
```

### Frontend
- Alerts appear in real-time
- "Rapid Movements" stat counter increases
- Alert details show movement speed
- WebSocket connection shows alerts streaming

## Troubleshooting

### Still No Alerts?

**Check 1: Is pose being detected?**
Look for: `Frame X: Pose detected, Movement speed: ...`
- If YES → Pose detection works, check threshold
- If NO → Video might not have clear view of person

**Check 2: What's the movement speed?**
Look at the speed values in terminal
- If < 0.08 → Movement too slow, need even lower threshold
- If > 0.08 → Should trigger alert, check alert generation

**Check 3: Is video being processed?**
Look for: `Processing video: ...`
- If YES → Video upload works
- If NO → Check file upload

**Check 4: Are alerts being generated?**
Look for: `ALERT: Rapid movement detected...`
- If YES → Backend works, check frontend WebSocket
- If NO → Movement not rapid enough or pose not detected

### Adjust Threshold Further

If still no alerts, make it even more sensitive:

In `backend/main.py`, line ~105:
```python
self.rapid_movement_threshold = 0.05  # Even more sensitive
```

Then restart backend again.

### Check Video Quality

For best results, video should have:
- ✅ Clear view of person
- ✅ Good lighting
- ✅ Person visible from head to hips
- ✅ Actual movement (not just camera shake)
- ✅ At least 30 FPS

## Quick Commands

**Stop backend:**
```powershell
# Find PID
Get-Process python

# Stop it
Stop-Process -Id <PID>
```

**Start backend:**
```bash
cd backend
python main.py
```

**Check if running:**
```powershell
curl http://localhost:8000/api/health
```

**View uploaded videos:**
```bash
dir backend\uploads
```

---

After restarting, try uploading your video again and watch the backend terminal for debug output!
