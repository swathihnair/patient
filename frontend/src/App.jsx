import { useState, useEffect, useRef } from 'react';
import './index.css';
import GeneralWard from './GeneralWard';

const API_URL = 'http://localhost:8000';
const GOOGLE_SHEETS_API = 'https://script.google.com/macros/s/AKfycbzKNdi0sXDXkcGLjKoP14deTqwITXq_lIvkCAvIXUJgKr9lk0ICd-SRwCcz4Vr5DbQZ/exec';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [patientDetails, setPatientDetails] = useState(null);
  const [loadingPatient, setLoadingPatient] = useState(false);
  const [stats, setStats] = useState({
    totalAlerts: 0,
    fallCount: 0,
    rapidMovementCount: 0,
    seizureCount: 0,
    bedExitCount: 0,
    abnormalPostureCount: 0,
    breathingAlertCount: 0,
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
          seizureCount: alert.type === 'SEIZURE' ? prev.seizureCount + 1 : prev.seizureCount,
          bedExitCount: alert.type === 'BED_EXIT' ? prev.bedExitCount + 1 : prev.bedExitCount,
          abnormalPostureCount: alert.type === 'ABNORMAL_POSTURE' ? prev.abnormalPostureCount + 1 : prev.abnormalPostureCount,
          breathingAlertCount: alert.type === 'ABNORMAL_BREATHING' ? prev.breathingAlertCount + 1 : prev.breathingAlertCount,
        }));

        // Update room status
        setRooms(prev => prev.map(room =>
          room.id === selectedRoom
            ? { ...room, status: alert.severity === 'CRITICAL' || alert.severity === 'HIGH' ? 'alert' : 'warning', lastAlert: alert }
            : room
        ));

        // Fetch patient details when alert is received
        fetchPatientDetails(selectedRoom);

        // Play alert sound
        if (alert.severity === 'CRITICAL' || alert.severity === 'HIGH') {
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

  const fetchPatientDetails = async (roomId) => {
    setLoadingPatient(true);
    try {
      // Fetch patient details from Google Sheets
      const response = await fetch(`${GOOGLE_SHEETS_API}?room=${roomId}`);
      const data = await response.json();
      
      if (data && data.length > 0) {
        setPatientDetails(data[0]); // Assuming first match is the patient
      } else {
        setPatientDetails({
          name: `Patient in Room ${roomId}`,
          room: `Room ${100 + roomId}`,
          age: 'N/A',
          condition: 'N/A',
          notes: 'No patient data found'
        });
      }
    } catch (error) {
      console.error('Error fetching patient details:', error);
      setPatientDetails({
        name: `Patient in Room ${roomId}`,
        room: `Room ${100 + roomId}`,
        error: 'Failed to load patient details'
      });
    } finally {
      setLoadingPatient(false);
    }
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
        fallCount: processResult.summary.fall_count || 0,
        rapidMovementCount: processResult.summary.rapid_movement_count || 0,
        seizureCount: processResult.summary.seizure_count || 0,
        bedExitCount: processResult.summary.bed_exit_count || 0,
        abnormalPostureCount: processResult.summary.abnormal_posture_count || 0,
        breathingAlertCount: processResult.summary.abnormal_breathing_count || 0,
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
      seizureCount: 0,
      bedExitCount: 0,
      abnormalPostureCount: 0,
      breathingAlertCount: 0,
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
                onClick={() => {
                  setSelectedRoom(room.id);
                  setPatientDetails(null); // Clear patient details when switching rooms
                }}
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
                
                {/* Patient Details - Shows when room is selected */}
                {selectedRoom === room.id && (
                  <div className="room-patient-details">
                    {!patientDetails ? (
                      <button 
                        className="btn-load-patient"
                        onClick={(e) => {
                          e.stopPropagation();
                          fetchPatientDetails(room.id);
                        }}
                        disabled={loadingPatient}
                      >
                        {loadingPatient ? (
                          <>
                            <span className="loading-small"></span>
                            Loading...
                          </>
                        ) : (
                          <>
                            👤 Load Patient Details
                          </>
                        )}
                      </button>
                    ) : (
                      <>
                        <div className="patient-detail-row">
                          <span className="detail-label">ID:</span>
                          <span className="detail-value">{patientDetails['patient id'] || patientDetails.patientId || 'N/A'}</span>
                        </div>
                        <div className="patient-detail-row">
                          <span className="detail-label">Name:</span>
                          <span className="detail-value">{patientDetails['patient name'] || patientDetails.patientName || patientDetails.name || 'N/A'}</span>
                        </div>
                        <div className="patient-detail-row">
                          <span className="detail-label">Room:</span>
                          <span className="detail-value">{patientDetails['room no'] || patientDetails.roomNo || patientDetails.room || 'N/A'}</span>
                        </div>
                        <div className="patient-detail-row">
                          <span className="detail-label">Disease:</span>
                          <span className="detail-value">{patientDetails.disease || 'N/A'}</span>
                        </div>
                        <div className="patient-detail-row">
                          <span className="detail-label">Doctor:</span>
                          <span className="detail-value">{patientDetails['doctor name'] || patientDetails.doctorName || 'N/A'}</span>
                        </div>
                        <div className="patient-detail-row">
                          <span className="detail-label">Bystander:</span>
                          <span className="detail-value">{patientDetails.bystander || 'N/A'}</span>
                        </div>
                        <button 
                          className="btn-refresh-patient"
                          onClick={(e) => {
                            e.stopPropagation();
                            fetchPatientDetails(room.id);
                          }}
                          disabled={loadingPatient}
                        >
                          🔄 Refresh
                        </button>
                      </>
                    )}
                  </div>
                )}
                
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
              🚨
            </div>
            <div className="stat-value">{stats.fallCount}</div>
            <div className="stat-label">Fall Incidents</div>
          </div>

          <div className="card stat-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, hsl(280, 80%, 60%), hsl(300, 80%, 60%))' }}>
              💥
            </div>
            <div className="stat-value">{stats.seizureCount}</div>
            <div className="stat-label">Seizure Alerts</div>
          </div>

          <div className="card stat-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, hsl(30, 90%, 55%), hsl(50, 90%, 55%))' }}>
              🚪
            </div>
            <div className="stat-value">{stats.bedExitCount}</div>
            <div className="stat-label">Bed Exits</div>
          </div>

          <div className="card stat-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, hsl(40, 90%, 55%), hsl(60, 90%, 55%))' }}>
              ⚡
            </div>
            <div className="stat-value">{stats.rapidMovementCount}</div>
            <div className="stat-label">Rapid Movements</div>
          </div>

          <div className="card stat-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, hsl(260, 70%, 60%), hsl(280, 70%, 60%))' }}>
              🤸
            </div>
            <div className="stat-value">{stats.abnormalPostureCount}</div>
            <div className="stat-label">Abnormal Posture</div>
          </div>

          <div className="card stat-card">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, hsl(180, 70%, 55%), hsl(200, 70%, 55%))' }}>
              🫁
            </div>
            <div className="stat-value">{stats.breathingAlertCount}</div>
            <div className="stat-label">Breathing Alerts</div>
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
                        {alert.type === 'FALL' ? '🚨' : 
                         alert.type === 'SEIZURE' ? '💥' :
                         alert.type === 'BED_EXIT' ? '🚪' :
                         alert.type === 'ABNORMAL_POSTURE' ? '🤸' :
                         alert.type === 'ABNORMAL_BREATHING' ? '🫁' : '⚡'}
                      </span>
                      <span>{alert.type.replace(/_/g, ' ')}</span>
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
                    {alert.distance && (
                      <span>📏 Distance: {(alert.distance * 100).toFixed(1)}%</span>
                    )}
                    {alert.posture_type && (
                      <span>🤸 Type: {alert.posture_type}</span>
                    )}
                    {alert.breathing_rate && (
                      <span>🫁 Rate: {alert.breathing_rate.toFixed(1)} bpm ({alert.status})</span>
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
