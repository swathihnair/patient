# Testing Guide - Advanced AI Detection Features

## Quick Start

### 1. Start the Backend
```bash
cd backend
python main.py
```
Backend should start on `http://localhost:8000`

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```
Frontend should start on `http://localhost:5175`

### 3. Open Browser
Navigate to `http://localhost:5175`

## Testing Each Feature

### ✅ Fall Detection
**What to test**: Patient falling from bed or lying horizontally

**Expected behavior**:
- Alert type: `FALL`
- Severity: `CRITICAL`
- Icon: 🚨
- Message: "🚨 Fall detected - Immediate attention required!"
- Stat card: "Fall Incidents" counter increases
- Visual overlay: "FALL DETECTED!" text on video

**Test video requirements**:
- Patient's nose should be close to hip level (horizontal position)
- Hip position should be low in frame (y > 0.7)

---

### ✅ Seizure Detection
**What to test**: Rapid, erratic, convulsive movements

**Expected behavior**:
- Alert type: `SEIZURE`
- Severity: `CRITICAL`
- Icon: 💥
- Message: "🚨 Seizure detected - Emergency response needed!"
- Stat card: "Seizure Alerts" counter increases
- Visual overlay: "SEIZURE DETECTED!" text on video

**Test video requirements**:
- High variance in body part positions
- Consistent high movement across multiple frames (20+ frames)
- Erratic shoulder and hip movements

---

### ✅ Bed Exit Detection
**What to test**: Patient leaving the bed area

**Expected behavior**:
- Alert type: `BED_EXIT`
- Severity: `HIGH`
- Icon: 🚪
- Message: "⚠️ Patient left bed - Check immediately!"
- Stat card: "Bed Exits" counter increases
- Visual overlay: "BED EXIT DETECTED!" text on video
- Alert details show distance from bed center

**Test video requirements**:
- Patient should start in bed (system learns bed region)
- Patient moves outside the bed boundaries
- Hip position moves beyond ±0.2 from initial position

---

### ✅ Abnormal Posture Detection
**What to test**: Unusual body positions

**Expected behavior**:
- Alert type: `ABNORMAL_POSTURE`
- Severity: `MEDIUM`
- Icon: 🤸
- Message: "⚠️ Abnormal posture detected: [Type]"
- Stat card: "Abnormal Posture" counter increases
- Visual overlay: "ABNORMAL POSTURE: [Type]" text on video
- Alert details show posture type

**Posture types detected**:
1. **Upside Down**: Head below hips
2. **Extreme Lean**: Shoulders tilted > 0.15
3. **Twisted Body**: Shoulders/hips misaligned > 0.2
4. **Curled Up**: Body height < 0.15

**Test video requirements**:
- Patient in unusual positions
- Clear visibility of shoulders and hips

---

### ✅ Rapid Movement Detection
**What to test**: Fast patient movements

**Expected behavior**:
- Alert type: `RAPID_MOVEMENT`
- Severity: `MEDIUM`
- Icon: ⚡
- Message: "⚡ Rapid movement detected - Check patient"
- Stat card: "Rapid Movements" counter increases
- Alert details show movement speed

**Test video requirements**:
- Quick position changes
- Movement speed > 0.15 (normalized)

---

### ✅ Breathing Rate Monitoring
**What to test**: Abnormal breathing patterns

**Expected behavior**:
- Alert type: `ABNORMAL_BREATHING`
- Severity: `HIGH`
- Icon: 🫁
- Message: "⚠️ Abnormal breathing: [Rate] bpm ([Status])"
- Stat card: "Breathing Alerts" counter increases
- Visual overlay: "Breathing: [Rate] bpm ([Status])" at bottom
- Alert details show breathing rate and status

**Breathing classifications**:
- **Slow (Bradypnea)**: < 12 bpm
- **Normal**: 12-20 bpm
- **Fast (Tachypnea)**: > 20 bpm

**Alert triggers**:
- < 10 bpm OR > 25 bpm

**Test video requirements**:
- Visible chest/shoulder movement
- At least 30 frames of data for calculation
- Clear view of shoulders

---

## UI Testing Checklist

### Dashboard
- [ ] All 7 stat cards display correctly
- [ ] Stat counters update in real-time
- [ ] Icons match alert types
- [ ] Gradient colors display properly

### Alert List
- [ ] Alerts appear in real-time via WebSocket
- [ ] Alert icons match type (🚨💥🚪🤸⚡🫁)
- [ ] Severity badges show correct color
- [ ] Alert details show relevant metrics
- [ ] Timestamp formats correctly
- [ ] Frame numbers display
- [ ] Confidence/speed/distance show when available
- [ ] Posture type shows for abnormal posture
- [ ] Breathing rate shows for breathing alerts

### Room Cards
- [ ] Room status updates on alert
- [ ] Patient details fetch on alert
- [ ] Patient details display below video
- [ ] Alert animation plays for critical/high severity
- [ ] Last alert shows in room card

### Upload & Processing
- [ ] Video upload works
- [ ] Processing shows loading state
- [ ] Summary stats populate after processing
- [ ] All alert types counted correctly

### WebSocket
- [ ] Connection status shows "Connected"
- [ ] Real-time alerts stream correctly
- [ ] Reconnection works after disconnect
- [ ] Alert sound plays for critical/high severity

---

## Sample Test Workflow

### Test 1: Upload Pre-recorded Video
1. Select a room (e.g., Room 101)
2. Click "Choose File" or drag-drop video
3. Click "Analyze Video"
4. Wait for processing
5. Verify alerts appear
6. Check stat counters
7. Verify patient details load

### Test 2: Real-time Monitoring
1. Upload video with multiple alert types
2. Watch alerts stream in real-time
3. Verify WebSocket connection
4. Check alert sounds play
5. Verify room status updates
6. Check patient details display

### Test 3: Multiple Rooms
1. Upload different videos to different rooms
2. Switch between rooms
3. Verify alerts are room-specific
4. Check stat counters aggregate correctly

---

## Expected Alert Counts

For a comprehensive test video (2-3 minutes), you might see:
- **Falls**: 1-3 alerts
- **Seizures**: 0-2 alerts (rare)
- **Bed Exits**: 1-2 alerts
- **Abnormal Posture**: 3-10 alerts
- **Rapid Movements**: 5-15 alerts
- **Breathing Alerts**: 0-5 alerts

---

## Troubleshooting

### No Alerts Generated
- Check MediaPipe is installed: `pip list | grep mediapipe`
- Verify pose detection model downloaded: `backend/pose_landmarker.task`
- Check video has clear view of patient
- Verify patient is visible in frame

### WebSocket Not Connecting
- Check backend is running on port 8000
- Verify CORS settings allow frontend origin
- Check browser console for errors

### Patient Details Not Loading
- Verify Google Sheets API URL is correct
- Check room number matches sheet data
- Verify internet connection

### Alerts Not Displaying
- Check browser console for errors
- Verify alert type matches expected types
- Check severity level is valid

---

## Performance Notes

- **Frame Processing**: Every 5th frame processed for performance
- **Buffer Sizes**: 
  - Movement: 10 frames
  - Seizure: 30 frames
  - Breathing: 60 frames
- **Video Resolution**: Higher resolution = slower processing
- **Recommended**: 720p or lower for real-time processing

---

## Next Steps After Testing

1. **Adjust Thresholds**: Fine-tune detection sensitivity in `backend/main.py`
2. **Add Test Videos**: Create library of test videos for each alert type
3. **Implement Face Recognition**: Add patient identification feature
4. **Database Integration**: Store alerts for historical analysis
5. **Alert Filtering**: Add UI controls to filter by type/severity
6. **Export Reports**: Generate PDF summaries of monitoring sessions

---

## Support

If you encounter issues:
1. Check browser console (F12)
2. Check backend terminal output
3. Verify all dependencies installed
4. Review `AI_DETECTION_FEATURES.md` for implementation details
