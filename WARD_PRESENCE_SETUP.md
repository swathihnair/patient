# Ward Patient Presence Detection Setup

This guide will help you set up the single-image ward patient presence detection feature using Gemini AI.

## Features

- Upload a single ward image
- AI analyzes patient presence at each bed
- Identifies empty beds with specific locations
- Shows statistics (total beds, occupied, empty)
- Real-time analysis using Google's Gemini AI

## Setup Instructions

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure Backend

1. Navigate to the `backend` folder
2. Copy `.env.example` to `.env`:
   ```cmd
   copy .env.example .env
   ```

3. Open `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Install Dependencies

Install the required Python packages:

```cmd
cd backend
pip install -r requirements.txt
```

### 4. Start Backend Server

```cmd
python main.py
```

The backend will start on `http://localhost:8000`

### 5. Start Frontend

In a new terminal:

```cmd
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`

## How to Use

1. Open the application in your browser
2. Navigate to "General Ward" section
3. Set the expected number of beds (default: 10)
4. Click to upload a ward image
5. Click "Analyze Patient Presence"
6. View results showing:
   - Summary of ward status
   - Total beds, occupied beds, empty beds
   - Specific locations of empty beds

## API Endpoint

**POST** `/api/analyze-ward-presence`

**Parameters:**
- `image`: Image file (multipart/form-data)
- `expected_beds`: Number of expected beds (default: 10)

**Response:**
```json
{
  "success": true,
  "analysis": {
    "summary": "Brief overview",
    "total_beds": 10,
    "occupied_beds": 8,
    "empty_beds": 2,
    "empty_spots": [
      {
        "location": "Bed 3 - Left side",
        "description": "Empty bed near the window"
      }
    ]
  }
}
```

## Troubleshooting

**Error: GEMINI_API_KEY not configured**
- Make sure you've added your API key to the `.env` file
- Restart the backend server after adding the key

**Error: Module not found**
- Run `pip install -r requirements.txt` in the backend folder
- Make sure you're using Python 3.8 or higher

**Image upload fails**
- Check that the backend server is running
- Verify CORS settings in `main.py`
- Ensure the image file is a valid format (JPG, PNG)

## Notes

- The Gemini API has rate limits on the free tier
- For production use, consider implementing caching
- Image analysis typically takes 2-5 seconds
- Larger images may take longer to process
