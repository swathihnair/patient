# General Ward - AI-Powered Patient Presence Detection

## 🤖 Feature Overview

The General Ward feature uses **Google's Gemini AI** to compare two images of a hospital ward and automatically detect missing patients from their beds.

### How It Works:
1. Upload a "before" image (reference with all patients present)
2. Upload an "after" image (current state to check)
3. Gemini AI analyzes both images and identifies:
   - Which beds are empty in the current image
   - Specific bed numbers or locations of missing patients
   - Summary of changes detected

---

## 🔑 Setup Gemini API Key

To use this feature, you need a **free** Gemini API key from Google.

### Step 1: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated API key

### Step 2: Set the Environment Variable

#### **Windows (PowerShell)**:
```powershell
# Temporary (current session only)
$env:GEMINI_API_KEY="your-api-key-here"

# Permanent (add to system environment variables)
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here', 'User')
```

#### **Windows (Command Prompt)**:
```cmd
set GEMINI_API_KEY=your-api-key-here
```

#### **Linux/Mac**:
```bash
# Temporary
export GEMINI_API_KEY="your-api-key-here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Restart the Backend

After setting the environment variable, restart the backend server:

```powershell
cd d:\demo\backend
.\venv\Scripts\activate
python main_simple.py
```

---

## 🎯 How to Use

1. **Open Dashboard**: Go to http://localhost:5173
2. **Select View Mode**: Click the dropdown in the header and select "General Ward"
3. **Upload Images**:
   - Click the first box to upload the "before" image (reference)
   - Click the second box to upload the "after" image (current state)
4. **Analyze**: Click "Compare Images with Gemini AI"
5. **View Results**: See which patients are missing and from which beds

---

## 📊 Example Use Cases

### Scenario 1: Patient Left Bed
- **Before**: All 4 beds occupied
- **After**: Bed 3 is empty
- **Result**: "Patient missing from Bed 3 - Immediate attention required"

### Scenario 2: Multiple Missing Patients
- **Before**: Ward with 6 patients
- **After**: 2 beds empty
- **Result**: Lists both missing patients with bed numbers

### Scenario 3: No Changes
- **Before**: All beds occupied
- **After**: All beds still occupied
- **Result**: "All patients present - No action needed"

---

## 🔒 Security Notes

- **API Key**: Keep your Gemini API key private
- **Free Tier**: Gemini API has a generous free tier
- **Rate Limits**: Be aware of API rate limits for production use
- **Data Privacy**: Images are temporarily saved locally and sent to Google's Gemini API

---

## 🛠️ Troubleshooting

### Error: "Gemini AI not configured"
**Solution**: Make sure you've set the `GEMINI_API_KEY` environment variable and restarted the backend.

### Error: "API key invalid"
**Solution**: Double-check your API key is correct and active at [Google AI Studio](https://makersuite.google.com/app/apikey).

### Images not uploading
**Solution**: Make sure images are in common formats (JPG, PNG, WebP) and under 10MB.

---

## 📁 File Structure

```
backend/
├── main_simple.py          # Backend with Gemini integration
└── ward_images/            # Uploaded ward images stored here

frontend/
├── src/
│   ├── GeneralWard.jsx     # General Ward component
│   └── GeneralWard.css     # Styles for General Ward
```

---

## 🚀 Future Enhancements

- Real-time CCTV integration
- Automatic periodic checks
- SMS/Email alerts for missing patients
- Historical tracking of patient movements
- Integration with hospital management systems

---

## 📞 Support

For issues or questions:
1. Check the console for error messages (F12 in browser)
2. Verify API key is set correctly
3. Check backend logs for detailed error information

**Your AI-powered patient safety system is ready!** 🏥✨
