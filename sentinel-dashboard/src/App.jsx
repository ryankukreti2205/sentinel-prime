import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [logs, setLogs] = useState([])
  const [isLive, setIsLive] = useState(false)
  const [videoSrc, setVideoSrc] = useState(null)
  const [uploading, setUploading] = useState(false)
  
  // Ref for the hidden file input
  const fileInputRef = useRef(null)

  // URLS
  const NODE_API = "http://localhost:5050/api/logs"
  const PYTHON_API = "http://localhost:5001"

  // 1. Handle File Upload
  const handleFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      // Send file to Python
      await axios.post(`${PYTHON_API}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      // If success, set the video source to the Python Stream URL
      setVideoSrc(`${PYTHON_API}/video_feed?t=${Date.now()}`)
    } catch (error) {
      console.error("Upload failed", error)
      alert("Failed to upload video to Python server.")
    } finally {
      setUploading(false)
    }
  }

  // 2. Handle Close (Reset UI)
  const handleClose = () => {
    setVideoSrc(null)
    setLogs([]) // Optional: Clear logs when closing
    setIsLive(false)
    
    // Reset the file input so you can upload the same file again if needed
    if (fileInputRef.current) {
        fileInputRef.current.value = ""
    }
  }

  // 3. Fetch Logs
  const fetchLogs = async () => {
    try {
      const response = await axios.get(NODE_API)
      const data = response.data
      setLogs(data)
      if (data.length > 0) {
        const diff = (new Date().getTime() - new Date(data[0].timestamp).getTime()) / 1000
        setIsLive(diff < 5)
      }
    } catch (error) {
      console.error("Error fetching logs", error)
    }
  }

  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="dashboard-container">
      
      {/* HEADER */}
      <header className="navbar">
        <div className="brand">🛡️ SENTINEL <span style={{fontWeight: 300}}>PRIME</span></div>
        <div className={`status-pill ${isLive ? 'active' : ''}`}>
          <div className="dot"></div>
          {isLive ? "EMERGENCY ACTIVE" : "SYSTEM STANDBY"}
        </div>
      </header>

      {/* MAIN CONTENT CENTERED */}
      <main className="content-centered">
        
        {/* VIDEO PLAYER SECTION */}
        <div className="video-section">
          <div className="video-wrapper">
            
            {/* CLOSE BUTTON (Only visible when videoSrc exists) */}
            {videoSrc && (
                <button className="close-btn" onClick={handleClose}>
                    ✕
                </button>
            )}

            {videoSrc ? (
              <img src={videoSrc} alt="Live AI Stream" className="live-feed" />
            ) : (
              <div className="placeholder" onClick={() => fileInputRef.current.click()}>
                <div className="placeholder-content">
                  <span style={{fontSize: '3rem', cursor: 'pointer'}}>📂</span>
                  <p>Click to Upload Traffic Video</p>
                </div>
              </div>
            )}
          </div>

          {/* HIDDEN INPUT */}
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            style={{display: 'none'}} 
            accept="video/*"
          />

          {/* UPLOAD BUTTON (Only show if NO video is playing) */}
          {!videoSrc && (
            <button 
              className="upload-btn" 
              onClick={() => fileInputRef.current.click()}
              disabled={uploading}
            >
              {uploading ? "UPLOADING..." : "📂 UPLOAD FOOTAGE"}
            </button>
          )}
        </div>

        {/* LOGS SECTION */}
        <div className="logs-section">
          <h3>Live Activity Feed</h3>
          <div className="logs-list">
            {logs.slice(0, 5).map((log, i) => (
              <div key={i} className="log-item">
                <span className="time">{new Date(log.timestamp).toLocaleTimeString()}</span>
                <span className="status">DETECTED</span>
              </div>
            ))}
            {logs.length === 0 && <div className="log-item" style={{justifyContent: 'center', color: '#444'}}>Waiting for signal...</div>}
          </div>
        </div>

      </main>
    </div>
  )
}

export default App