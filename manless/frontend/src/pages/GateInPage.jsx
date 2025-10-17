// Gate In Page - Kiosk untuk Gate Masuk
// Otomatis connect ke WebSocket channel gate_in berdasarkan URL

import React, { useState, useEffect } from 'react'
import { useSmartWebSocket } from '../services/smartWebSocket'

const GateInPage = () => {
  const ws = useSmartWebSocket()
  
  // State untuk UI
  const [connected, setConnected] = useState(false)
  const [hardwareStatus, setHardwareStatus] = useState({})
  const [gateStatus, setGateStatus] = useState('unknown')
  const [lastCardId, setLastCardId] = useState(null)
  const [logs, setLogs] = useState([])
  
  useEffect(() => {
    console.log('🚀 Gate IN Page - Initializing WebSocket...')
    
    // Connect to WebSocket
    ws.connect()
    
    // Setup event listeners
    ws.on('connected', (data) => {
      console.log('✅ Gate IN connected:', data)
      setConnected(true)
      addLog('WebSocket connected to gate_in', 'info')
    })
    
    ws.on('disconnected', (data) => {
      console.log('🔌 Gate IN disconnected:', data)
      setConnected(false)
      addLog('WebSocket disconnected', 'warning')
    })
    
    ws.on('hardware_status', (data) => {
      console.log('📊 Gate IN hardware status:', data.payload)
      setHardwareStatus(data.payload)
      
      // Extract gate status if available
      if (data.payload.arduino && data.payload.arduino.gate) {
        setGateStatus(data.payload.arduino.gate.status || 'unknown')
      }
    })
    
    ws.on('system_status', (data) => {
      console.log('🖥️ Gate IN system status:', data.payload)
      setHardwareStatus(data.payload)
    })
    
    ws.on('card_detected', (data) => {
      console.log('💳 Card detected at Gate IN:', data.payload)
      setLastCardId(data.payload.card_id)
      addLog(`Card detected: ${data.payload.card_id}`, 'success')
    })
    
    ws.on('parking_event', (data) => {
      console.log('🅿️ Parking event at Gate IN:', data.payload)
      if (data.payload.event_type === 'parking_entry') {
        addLog(`Parking entry: ${data.payload.data.card_id}`, 'success')
      }
    })
    
    ws.on('gate_control_response', (data) => {
      console.log('🚪 Gate control response:', data.payload)
      addLog(`Gate ${data.payload.action}: ${data.payload.success ? 'Success' : 'Failed'}`, 
        data.payload.success ? 'success' : 'error')
    })
    
    ws.on('error', (data) => {
      console.error('❌ Gate IN WebSocket error:', data)
      addLog(`Error: ${data.error}`, 'error')
    })
    
    // Cleanup on unmount
    return () => {
      console.log('🧹 Gate IN Page - Cleanup')
      ws.disconnect()
    }
  }, [])
  
  const addLog = (message, type = 'info') => {
    const newLog = {
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      message,
      type
    }
    setLogs(prev => [newLog, ...prev.slice(0, 9)]) // Keep last 10 logs
  }
  
  const handleOpenGate = () => {
    console.log('🚪 Opening Gate IN...')
    ws.openGate(10)
    addLog('Gate open command sent', 'info')
  }
  
  const handleCloseGate = () => {
    console.log('🚪 Closing Gate IN...')
    ws.closeGate()
    addLog('Gate close command sent', 'info')
  }
  
  const handleCaptureImage = () => {
    console.log('📸 Capturing image at Gate IN...')
    ws.captureImage()
    addLog('Image capture command sent', 'info')
  }
  
  const handleRefreshStatus = () => {
    console.log('🔄 Refreshing status...')
    ws.requestStatus()
    addLog('Status refresh requested', 'info')
  }
  
  const getStatusColor = (status) => {
    switch (status) {
      case true:
      case 'connected':
      case 'open':
        return 'green'
      case false:
      case 'disconnected':
      case 'closed':
        return 'red'
      default:
        return 'orange'
    }
  }
  
  const getLogColor = (type) => {
    switch (type) {
      case 'success': return '#4CAF50'
      case 'error': return '#F44336'
      case 'warning': return '#FF9800'
      default: return '#2196F3'
    }
  }
  
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <div style={{ 
        backgroundColor: '#1976D2', 
        color: 'white', 
        padding: '20px', 
        borderRadius: '8px',
        marginBottom: '20px',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: 0 }}>🚗 GATE MASUK</h1>
        <p style={{ margin: '5px 0 0 0' }}>Kiosk Parkir Manless</p>
        <div style={{ 
          marginTop: '10px',
          fontSize: '14px',
          opacity: 0.9
        }}>
          WebSocket: {connected ? '🟢 Connected' : '🔴 Disconnected'} | 
          Channel: {ws.getCurrentChannel()} |
          Gate: <span style={{color: getStatusColor(gateStatus)}}>{gateStatus.toUpperCase()}</span>
        </div>
      </div>
      
      {/* Control Panel */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '20px',
        marginBottom: '20px'
      }}>
        {/* Gate Controls */}
        <div style={{ 
          backgroundColor: '#f5f5f5', 
          padding: '20px', 
          borderRadius: '8px' 
        }}>
          <h3 style={{ margin: '0 0 15px 0' }}>🚪 Kontrol Gate</h3>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
            <button 
              onClick={handleOpenGate}
              disabled={!connected}
              style={{
                flex: 1,
                padding: '12px',
                backgroundColor: connected ? '#4CAF50' : '#ccc',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: connected ? 'pointer' : 'not-allowed',
                fontSize: '16px'
              }}
            >
              ⬆️ BUKA GATE
            </button>
            <button 
              onClick={handleCloseGate}
              disabled={!connected}
              style={{
                flex: 1,
                padding: '12px',
                backgroundColor: connected ? '#F44336' : '#ccc',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: connected ? 'pointer' : 'not-allowed',
                fontSize: '16px'
              }}
            >
              ⬇️ TUTUP GATE
            </button>
          </div>
          <button 
            onClick={handleCaptureImage}
            disabled={!connected}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: connected ? '#2196F3' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: connected ? 'pointer' : 'not-allowed',
              fontSize: '16px'
            }}
          >
            📸 AMBIL FOTO
          </button>
        </div>
        
        {/* Hardware Status */}
        <div style={{ 
          backgroundColor: '#f5f5f5', 
          padding: '20px', 
          borderRadius: '8px' 
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3 style={{ margin: 0 }}>⚙️ Status Hardware</h3>
            <button 
              onClick={handleRefreshStatus}
              disabled={!connected}
              style={{
                padding: '5px 10px',
                backgroundColor: '#9E9E9E',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: connected ? 'pointer' : 'not-allowed',
                fontSize: '12px'
              }}
            >
              🔄 Refresh
            </button>
          </div>
          
          <div style={{ fontSize: '14px' }}>
            <div style={{ marginBottom: '8px' }}>
              <span style={{ fontWeight: 'bold' }}>Arduino: </span>
              <span style={{ color: getStatusColor(hardwareStatus.arduino?.connected) }}>
                {hardwareStatus.arduino?.connected ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
            </div>
            
            <div style={{ marginBottom: '8px' }}>
              <span style={{ fontWeight: 'bold' }}>Camera: </span>
              <span style={{ color: getStatusColor(hardwareStatus.camera?.connected) }}>
                {hardwareStatus.camera?.connected ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
            </div>
            
            <div style={{ marginBottom: '8px' }}>
              <span style={{ fontWeight: 'bold' }}>Card Reader: </span>
              <span style={{ color: getStatusColor(hardwareStatus.card_reader?.connected) }}>
                {hardwareStatus.card_reader?.connected ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
            </div>
            
            {lastCardId && (
              <div style={{ 
                marginTop: '10px',
                padding: '8px',
                backgroundColor: '#E8F5E8',
                borderRadius: '4px',
                border: '1px solid #4CAF50'
              }}>
                <span style={{ fontWeight: 'bold' }}>Last Card: </span>
                {lastCardId}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Activity Logs */}
      <div style={{ 
        backgroundColor: '#f5f5f5', 
        padding: '20px', 
        borderRadius: '8px' 
      }}>
        <h3 style={{ margin: '0 0 15px 0' }}>📋 Activity Log</h3>
        <div style={{ 
          maxHeight: '200px', 
          overflowY: 'auto',
          backgroundColor: 'white',
          padding: '10px',
          borderRadius: '4px',
          border: '1px solid #ddd'
        }}>
          {logs.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              color: '#666', 
              fontStyle: 'italic' 
            }}>
              No activity yet...
            </div>
          ) : (
            logs.map(log => (
              <div 
                key={log.id}
                style={{ 
                  marginBottom: '5px',
                  fontSize: '12px',
                  padding: '5px',
                  borderLeft: `3px solid ${getLogColor(log.type)}`,
                  paddingLeft: '8px'
                }}
              >
                <span style={{ color: '#666' }}>[{log.timestamp}]</span> {log.message}
              </div>
            ))
          )}
        </div>
      </div>
      
      {/* Debug Info (dapat dihapus di production) */}
      <div style={{ 
        marginTop: '20px',
        padding: '10px',
        backgroundColor: '#f0f0f0',
        borderRadius: '4px',
        fontSize: '12px',
        color: '#666'
      }}>
        <details>
          <summary style={{ cursor: 'pointer' }}>🔧 Debug Info</summary>
          <pre style={{ marginTop: '10px', overflow: 'auto' }}>
            {JSON.stringify({
              connected,
              channel: ws.getCurrentChannel(),
              hardwareStatus,
              gateStatus,
              lastCardId
            }, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  )
}

export default GateInPage 