# Patient Details Display Guide

## Overview
Patient details are now displayed in the room cards below the video preview. The system fetches patient information from your Google Sheets API when needed.

## How It Works

### 1. Automatic Display on Alert
When an alert is detected in a room, the system automatically:
- Fetches patient details from Google Sheets
- Displays the details below the video in the room card
- Shows: Patient ID, Name, Room No, Disease, Doctor Name, Bystander

### 2. Manual Load
You can also manually load patient details:
- Click on a room card to select it
- Click the "👤 Load Patient Details" button
- Patient details will be fetched and displayed

### 3. Refresh Details
If patient information changes:
- Click the "🔄 Refresh" button
- Updated details will be fetched from Google Sheets

## Patient Details Display

### Location
Patient details appear in the selected room card, below the video preview.

### Information Shown
```
┌─────────────────────────────────┐
│  Room Card (Selected)           │
├─────────────────────────────────┤
│  [Video Preview]                │
├─────────────────────────────────┤
│  Patient Details:               │
│  ┌───────────────────────────┐  │
│  │ ID:        P12345         │  │
│  │ Name:      John Doe       │  │
│  │ Room:      101            │  │
│  │ Disease:   Pneumonia      │  │
│  │ Doctor:    Dr. Smith      │  │
│  │ Bystander: Jane Doe       │  │
│  │ [🔄 Refresh]              │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

## Google Sheets API Integration

### API Endpoint
```
https://script.google.com/macros/s/AKfycbzKNdi0sXDXkcGLjKoP14deTqwITXq_lIvkCAvIXUJgKr9lk0ICd-SRwCcz4Vr5DbQZ/exec
```

### Request Format
```
GET ?room={roomId}
```

### Expected Response Format
```json
[
  {
    "patient id": "P12345",
    "patient name": "John Doe",
    "room no": "101",
    "disease": "Pneumonia",
    "doctor name": "Dr. Smith",
    "bystander": "Jane Doe"
  }
]
```

### Column Names (Case Insensitive)
The system supports multiple column name formats:
- **Patient ID**: `patient id`, `patientId`
- **Patient Name**: `patient name`, `patientName`, `name`
- **Room Number**: `room no`, `roomNo`, `room`
- **Disease**: `disease`
- **Doctor Name**: `doctor name`, `doctorName`
- **Bystander**: `bystander`

## User Interface

### States

#### 1. No Details Loaded
```
┌─────────────────────────────────┐
│  [👤 Load Patient Details]      │
└─────────────────────────────────┘
```

#### 2. Loading
```
┌─────────────────────────────────┐
│  [⏳ Loading...]                │
└─────────────────────────────────┘
```

#### 3. Details Loaded
```
┌─────────────────────────────────┐
│  ID:        P12345              │
│  Name:      John Doe            │
│  Room:      101                 │
│  Disease:   Pneumonia           │
│  Doctor:    Dr. Smith           │
│  Bystander: Jane Doe            │
│  [🔄 Refresh]                   │
└─────────────────────────────────┘
```

#### 4. Error State
```
┌─────────────────────────────────┐
│  ID:        N/A                 │
│  Name:      Patient in Room 101 │
│  Room:      Room 101            │
│  Error:     Failed to load      │
│  [🔄 Refresh]                   │
└─────────────────────────────────┘
```

## Workflow Examples

### Example 1: Alert Triggered
1. Video is being monitored in Room 101
2. Fall detected → Alert generated
3. System automatically fetches patient details for Room 101
4. Patient details appear below video in Room 101 card
5. Staff can see patient info immediately

### Example 2: Manual Check
1. Staff selects Room 102
2. Clicks "👤 Load Patient Details"
3. System fetches details from Google Sheets
4. Patient information displays
5. Staff can review patient info before monitoring

### Example 3: Update Information
1. Patient details are already displayed
2. Patient information changes in Google Sheets
3. Staff clicks "🔄 Refresh"
4. Updated details are fetched and displayed

## Features

### ✅ Automatic Fetch on Alert
- No manual action needed
- Details load when alert occurs
- Immediate access to patient info during emergencies

### ✅ Manual Load Button
- Load details anytime
- No need to wait for alert
- Proactive patient information access

### ✅ Refresh Capability
- Update details without page reload
- Sync with latest Google Sheets data
- Keep information current

### ✅ Room-Specific Details
- Each room shows its own patient
- Details clear when switching rooms
- No confusion between patients

### ✅ Error Handling
- Graceful fallback if API fails
- Shows "N/A" for missing data
- Retry option with refresh button

### ✅ Loading States
- Visual feedback during fetch
- Prevents multiple simultaneous requests
- Clear indication of system activity

## Styling

### Visual Design
- **Background**: Gradient (blue to purple)
- **Border**: Top border separates from video
- **Animation**: Smooth slide-in effect
- **Layout**: Clean, organized rows
- **Typography**: Clear labels and values

### Responsive
- Adapts to room card size
- Readable on all screen sizes
- Maintains layout integrity

## Testing

### Test Checklist
- [ ] Click room card → Details section appears
- [ ] Click "Load Patient Details" → Details fetch
- [ ] Alert occurs → Details auto-load
- [ ] Click "Refresh" → Details update
- [ ] Switch rooms → Details clear
- [ ] API fails → Error message shows
- [ ] Loading state → Spinner displays

### Test Data
Create test entries in Google Sheets:
```
Room 1: Patient A, Disease X, Dr. Smith
Room 2: Patient B, Disease Y, Dr. Jones
Room 3: Patient C, Disease Z, Dr. Brown
Room 4: Patient D, Disease W, Dr. Davis
```

## Troubleshooting

### Details Not Loading
**Problem**: Click "Load Patient Details" but nothing happens

**Solutions**:
1. Check browser console (F12) for errors
2. Verify Google Sheets API URL is correct
3. Test API directly in browser: `{API_URL}?room=1`
4. Check internet connection
5. Verify Google Sheets script is deployed

### Wrong Patient Details
**Problem**: Details show wrong patient

**Solutions**:
1. Check room number mapping in Google Sheets
2. Verify room ID matches sheet data
3. Click "Refresh" to reload
4. Check for duplicate entries in sheet

### "N/A" Showing
**Problem**: All fields show "N/A"

**Solutions**:
1. Check Google Sheets column names match expected format
2. Verify data exists for that room number
3. Check API response format
4. Ensure sheet is shared/published correctly

### Details Not Clearing
**Problem**: Old patient details remain when switching rooms

**Solutions**:
1. This should auto-clear - if not, refresh page
2. Check browser console for JavaScript errors
3. Verify latest code is deployed

## Configuration

### Update API URL
In `frontend/src/App.jsx`:
```javascript
const GOOGLE_SHEETS_API = 'YOUR_API_URL_HERE';
```

### Customize Fields
To add/remove fields, edit the patient details section in `App.jsx`:
```jsx
<div className="patient-detail-row">
  <span className="detail-label">Your Field:</span>
  <span className="detail-value">{patientDetails.yourField || 'N/A'}</span>
</div>
```

### Styling
Customize appearance in `frontend/src/index.css`:
```css
.room-patient-details {
  /* Your custom styles */
}
```

## Best Practices

### For Staff
1. **Load details proactively** - Don't wait for alerts
2. **Refresh periodically** - Keep info current
3. **Verify patient** - Check details match room
4. **Report issues** - If details seem wrong

### For Administrators
1. **Keep sheets updated** - Maintain accurate data
2. **Use consistent format** - Follow column naming
3. **Test regularly** - Verify API connectivity
4. **Monitor errors** - Check logs for issues

## Future Enhancements

### Planned Features
- [ ] Patient photo display
- [ ] Medical history timeline
- [ ] Medication schedule
- [ ] Vital signs integration
- [ ] Emergency contact info
- [ ] Allergy warnings
- [ ] Recent notes/observations

### Possible Improvements
- Cache patient details locally
- Offline mode with last-known data
- Real-time sync with Google Sheets
- Multiple patient views
- Export patient reports
- Print patient summary

---

## Quick Reference

**Load Details**: Click "👤 Load Patient Details" button
**Refresh**: Click "🔄 Refresh" button
**Auto-Load**: Happens automatically on alert
**Clear**: Switch to different room

**API**: Google Sheets Apps Script
**Fields**: ID, Name, Room, Disease, Doctor, Bystander
**Location**: Below video in selected room card

---

Patient details display is now fully functional and ready to use! 🎉
