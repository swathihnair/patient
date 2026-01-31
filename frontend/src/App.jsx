import { useState, useEffect, useRef } from 'react';
import './index.css';
import GeneralWard from './GeneralWard';

const API_URL = 'http://localhost:8000';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [stats, setStats] = useState({
    totalAlerts: 0,
    fallCount: 0,
    rapidMovementCount: 0,
  });
  const [connectionStatus, setConnectionStatus] = useState('Connecting...');
  const [rooms, setRooms] = useState([
    { id: 1, name: 'Room 101', patient: 'Patient A', status: 'monitoring', video: null, lastAlert: null },
    { id: 2, name: 'Room 102', patient: 'Patient B', status: 'normal', video: null, lastAlert: null },
    { id: 3, name: 'Room 103', patient: 'Patient C', status: 'normal', video: null, lastAlert: null },
    { id: 4, name: 'Room 104', patient: 'Patient D', status: 'normal', video: null, lastAlert: null },
  ]);
  const [selectedRoom, setSelectedRoom] = useState(1);
  const [viewMode, setViewMode] = useState('rooms'); // 'rooms' or 'general-ward'
  const wsRef = useRef(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  // WebSocket connection for real-time alerts
  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws/alerts');

      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('Connected');
      };

      ws.onmessage = (event) => {
        const alert = JSON.parse(event.data);
        console.log('Received alert:', alert);

        // Add new alert to the beginning of the list
        setAlerts(prev => [alert, ...prev]);

        // Update stats
        setStats(prev => ({
          totalAlerts: prev.totalAlerts + 1,
          fallCount: alert.type === 'FALL' ? prev.fallCount + 1 : prev.fallCount,
          rapidMovementCount: alert.type === 'RAPID_MOVEMENT' ? prev.rapidMovementCount + 1 : prev.rapidMovementCount,
        }));

        // Update room status
        setRooms(prev => prev.map(room =>
          room.id === selectedRoom
            ? { ...room, status: alert.severity === 'HIGH' ? 'alert' : 'warning', lastAlert: alert }
            : room
        ));

        // Play alert sound
        if (alert.severity === 'HIGH') {
          playAlertSound();
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('Error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('Disconnected');

        setTimeout(() => {
          console.log('Attempting to reconnect...');
          connectWebSocket();
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('Error');
    }
  };

  const playAlertSound = () => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800;
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
      setUploadedFile(file);
      // Create video preview
      const videoUrl = URL.createObjectURL(file);
      setRooms(prev => prev.map(room =>
        room.id === selectedRoom
          ? { ...room, video: videoUrl, status: 'monitoring' }
          : room
      ));
    } else {
      alert('Please select a valid video file');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('video/')) {
      setUploadedFile(file);
      const videoUrl = URL.createObjectURL(file);
      setRooms(prev => prev.map(room =>
        room.id === selectedRoom
          ? { ...room, video: videoUrl, status: 'monitoring' }
          : room
      ));
    } else {
      alert('Please drop a valid video file');
    }
  };

  const handleUpload = async () => {
    if (!uploadedFile) {
      alert('Please select a video file first');
      return;
    }

    setIsProcessing(true);
    console.log('Starting upload for file:', uploadedFile.name);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      console.log('Uploading to:', `${API_URL}/api/upload-video`);
      const uploadResponse = await fetch(`${API_URL}/api/upload-video`, {
        method: 'POST',
        body: formData,
      });

      console.log('Upload response status:', uploadResponse.status);

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed with status: ${uploadResponse.status}`);
      }

      const uploadResult = await uploadResponse.json();
      console.log('Upload result:', uploadResult);

      if (!uploadResult.success) {
        throw new Error(uploadResult.error || 'Upload failed');
      }

      console.log('Processing video:', uploadResult.filename);
      const processResponse = await fetch(
        `${API_URL}/api/process-video/${uploadResult.filename}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );

      console.log('Process response status:', processResponse.status);

      if (!processResponse.ok) {
        const errorText = await processResponse.text();
        console.error('Process error response:', errorText);
        throw new Error(`Processing failed with status: ${processResponse.status}`);
      }

      const processResult = await processResponse.json();
      console.log('Process result:', processResult);

      if (!processResult.success) {
        throw new Error(processResult.error || 'Processing failed');
      }

      setAlerts(processResult.alerts);
      setStats({
        totalAlerts: processResult.alerts.length,
        fallCount: processResult.summary.fall_count,
        rapidMovementCount: processResult.summary.rapid_movement_count,
      });

      // Update room status based on alerts
      const hasHighAlert = processResult.alerts.some(a => a.severity === 'HIGH');
      setRooms(prev => prev.map(room =>
        room.id === selectedRoom
          ? { ...room, status: hasHighAlert ? 'alert' : 'warning' }
          : room
      ));

      alert(`Processing complete! Found ${processResult.alerts.length} alerts.`);
    } catch (error) {
      console.error('Detailed error:', error);
      alert(`Error: ${error.message}\n\nCheck browser console (F12) for details.`);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (timestamp) => {
    if (typeof timestamp === 'number') {
      const minutes = Math.floor(timestamp / 60);
      const seconds = Math.floor(timestamp % 60);
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
    return new Date(timestamp).toLocaleTimeString();
  };

  const clearAlerts = () => {
    setAlerts([]);
    setStats({
      totalAlerts: 0,
      fallCount: 0,
      rapidMovementCount: 0,
    });
  };

  const getRoomStatusColor = (status) => {
    switch (status) {
      case 'alert': return 'hsl(0, 80%, 60%)';
      case 'warning': return 'hsl(40, 90%, 55%)';
      case 'monitoring': return 'hsl(200, 80%, 55%)';
      default: return 'hsl(140, 70%, 50%)';
    }
  };

  // If general ward mode, show the GeneralWard component
  if (viewMode === 'general-ward') {
    return <GeneralWard onBack={() => setViewMode('rooms')} />;
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">🏥</div>
            <div className="logo-text">
              <h1>Patient Monitor</h1>
              <p>Multi-Room Activity Detection</p>
            </div>
          </div>
        </div>
        <div className="header-right">
          <div className="view-mode-selector">
            <label htmlFor="viewMode">View:</label>
            <select
              id="viewMode"
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              className="view-mode-dropdown"
            >
              <option value="rooms">Individual Rooms</option>
              <option value="general-ward">General Ward</option>
            </select>
          </div>
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span className="status-text">{connectionStatus}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Room Grid */}
        <div className="rooms-section">
          <h2 className="section-title">
            {viewMode === 'general-ward' ? 'General Ward - All Patients' : 'Patient Rooms'}
          </h2>
          <div className="rooms-grid">
            {rooms.map(room => (
              <div
                key={room.id}
                className={`room-card ${selectedRoom === room.id ? 'selected' : ''} ${room.status}`}
                onClick={() => setSelectedRoom(room.id)}
                style={{ borderColor: selectedRoom === room.id ? getRoomStatusColor(room.status) : 'var(--border-color)' }}
              >
                <div className="room-header">
                  <div className="room-info">
                    <h3>{room.name}</h3>
                    <p>{room.patient}</p>
                  </div>
                  <div
                    className="room-status-badge"
                    style={{ background: getRoomStatusColor(room.status) }}
                  >
                    {room.status === 'alert' ? '🚨' : room.status === 'warning' ? '⚠️' : room.status === 'monitoring' ? '📹' : '✓'}
                  </div>
                </div>
                <div className="room-video">
                  {room.video ? (
                    <video
                      src={room.video}
                      className="video-preview"
                      muted
                      loop
                      autoPlay
                    />
                  ) : (
                    <div className="no-video">
                      <span className="no-video-icon">📹</span>
                      <span>No video</span>
                    </div>
                  )}
                </div>
                {room.lastAlert && (
                  <div className="room-last-alert">
                    Last: {room.lastAlert.type}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Stats Dashboard */}
        <div className="dashboard-grid">
          <div className="card stat-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, hsl(200, 80%, 55%), hsl(220, 80%, 55%))' }}>
              📊
            </div>
            <div className="stat-value">{stats.totalAlerts}</div>
            <div className="stat-label">Total Alerts</div>
          </div>

          <div className="card stat-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, hsl(0, 80%, 60%), hsl(20, 80%, 60%))' }}>
              ⚠️
            </div>
            <div className="stat-value">{stats.fallCount}</div>
            <div className="stat-label">Fall Incidents</div>
          </div>

          <div className="card stat-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, hsl(40, 90%, 55%), hsl(60, 90%, 55%))' }}>
              ⚡
            </div>
            <div className="stat-value">{stats.rapidMovementCount}</div>
            <div className="stat-label">Rapid Movements</div>
          </div>
        </div>

        {/* Upload Section */}
        <div
          className={`upload-section ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="upload-icon">📹</div>
          <div className="upload-text">
            <h3>
              Upload Video for {viewMode === 'general-ward' ? 'General Ward' : rooms.find(r => r.id === selectedRoom)?.name}
            </h3>
            <p>
              {uploadedFile
                ? `Selected: ${uploadedFile.name}`
                : 'Drag and drop a video file or click to browse'}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button
              className="btn btn-secondary"
              onClick={() => fileInputRef.current?.click()}
              disabled={isProcessing}
            >
              📁 Choose File
            </button>
            <button
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={!uploadedFile || isProcessing}
            >
              {isProcessing ? (
                <>
                  <span className="loading"></span>
                  Processing...
                </>
              ) : (
                <>
                  🚀 Analyze Video
                </>
              )}
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
          />
        </div>

        {/* Alerts List */}
        <div className="alerts-container">
          <div className="alerts-header">
            <h2 className="alerts-title">
              Activity Alerts - {viewMode === 'general-ward' ? 'General Ward' : rooms.find(r => r.id === selectedRoom)?.name}
            </h2>
            {alerts.length > 0 && (
              <button className="btn btn-secondary" onClick={clearAlerts}>
                🗑️ Clear All
              </button>
            )}
          </div>

          {alerts.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📭</div>
              <p>No alerts yet. Upload a video to start monitoring.</p>
            </div>
          ) : (
            <div>
              {alerts.map((alert, index) => (
                <div
                  key={index}
                  className={`alert-item ${alert.severity.toLowerCase()}`}
                >
                  <div className="alert-header">
                    <div className="alert-type">
                      <span>
                        {alert.type === 'FALL' ? '🚨' : '⚡'}
                      </span>
                      <span>{alert.type.replace('_', ' ')}</span>
                    </div>
                    <span className={`alert-badge ${alert.severity.toLowerCase()}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <div className="alert-message">{alert.message}</div>
                  <div className="alert-details">
                    <span>⏱️ {formatTime(alert.timestamp)}</span>
                    {alert.frame && <span>🎬 Frame {alert.frame}</span>}
                    {alert.confidence && (
                      <span>📊 Confidence: {(alert.confidence * 100).toFixed(1)}%</span>
                    )}
                    {alert.speed && (
                      <span>💨 Speed: {(alert.speed * 100).toFixed(1)}%</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
