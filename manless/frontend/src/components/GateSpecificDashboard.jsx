import React, { useState, useEffect } from 'react'
import { gateConfig } from '../services/gateConfig.js'
import { wsService } from '../services/websocket.js'
import { apiService } from '../services/api.js'
import GateSelector from './GateSelector.jsx'

const GateSpecificDashboard = () => {
  const [gateInfo, setGateInfo] = useState(gateConfig.getGateInfo())
  const [systemStatus, setSystemStatus] = useState(null)
  const [gateStatus, setGateStatus] = useState(null)
  const [recentEvents, setRecentEvents] = useState([])
  const [connectionStatus, setConnectionStatus] = useState('CONNECTING')
  const [parkingCount, setParkingCount] = useState({ total: 0, occupied: 0, available: 0 })

  useEffect(() => {
    // Set document title berdasarkan gate
    document.title = gateConfig.getDashboardTitle()
    
    // Set theme color
    const themeColor = gateConfig.getThemeColor()
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', themeColor)

    // Listen untuk gate changes
    const handleGateChange = (event) => {
      setGateInfo(event.detail.gateInfo)
      document.title = gateConfig.getDashboardTitle()
    }

    gateConfig.onGateChange(handleGateChange)

    return () => {
      gateConfig.offGateChange(handleGateChange)
    }
  }, [])

  useEffect(() => {
    // WebSocket event listeners
    const handleConnected = () => {
      setConnectionStatus('CONNECTED')
    }

    const handleDisconnected = () => {
      setConnectionStatus('DISCONNECTED')
    }

    const handleSystemStatus = (data) => {
      setSystemStatus(data)
      if (data.gates && data.gates[gateConfig.getCurrentGate()]) {
        setGateStatus(data.gates[gateConfig.getCurrentGate()])
      }
    }

    const handleParkingCapacity = (data) => {
      setParkingCount(data)
    }

    const handleParkingEvent = (data) => {
      // Tambahkan event ke recent events
      const newEvent = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: data.event,
        gate: data.gate,
        result: data.result,
        message: `${data.event === 'entry' ? 'Kendaraan Masuk' : 'Kendaraan Keluar'} - ${data.result.card_id || 'Unknown'}`
      }

      setRecentEvents(prev => [newEvent, ...prev.slice(0, 4)]) // Keep only 5 recent events
    }

    const handleError = (data) => {
      console.error('WebSocket Error:', data)
    }

    // Subscribe to WebSocket events
    wsService.on('connected', handleConnected)
    wsService.on('disconnected', handleDisconnected)
    wsService.on('system_status', handleSystemStatus)
    wsService.on('parking_capacity', handleParkingCapacity)
    wsService.on('parking_event', handleParkingEvent)
    wsService.on('error', handleError)

    // Initial data request
    wsService.requestSystemStatus()
    wsService.requestParkingCapacity()

    // Periodic updates
    const interval = setInterval(() => {
      wsService.requestSystemStatus()
      wsService.requestParkingCapacity()
    }, 10000) // Every 10 seconds

    return () => {
      wsService.off('connected', handleConnected)
      wsService.off('disconnected', handleDisconnected)
      wsService.off('system_status', handleSystemStatus)
      wsService.off('parking_capacity', handleParkingCapacity)
      wsService.off('parking_event', handleParkingEvent)
      wsService.off('error', handleError)
      clearInterval(interval)
    }
  }, [])

  const handleManualGateControl = async (action) => {
    try {
      if (action === 'open') {
        await wsService.controlGate(gateConfig.getCurrentGate(), 'open', 10)
      } else {
        await wsService.controlGate(gateConfig.getCurrentGate(), 'close')
      }
    } catch (error) {
      console.error('Gate control error:', error)
    }
  }

  const handleCaptureImage = async () => {
    try {
      await wsService.captureImage(gateConfig.getCurrentGate())
    } catch (error) {
      console.error('Capture image error:', error)
    }
  }

  const simulateCardScan = async () => {
    const cardId = `TEST_${Date.now()}`
    await wsService.simulateCardScan(gateConfig.getCurrentGate(), cardId, 'B1234XYZ')
  }

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'CONNECTED': return '#4CAF50'
      case 'DISCONNECTED': return '#F44336'
      default: return '#FF9800'
    }
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('id-ID')
  }

  return (
    <div className="gate-specific-dashboard" style={{
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      padding: '20px'
    }}>
      {/* Header */}
      <div className="dashboard-header" style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        borderLeft: `6px solid ${gateInfo.color}`
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '32px' }}>{gateInfo.icon}</span>
              <span>{gateInfo.name}</span>
            </h1>
            <p style={{ margin: 0, color: '#666' }}>
              📍 {gateInfo.location} • 🔗 Real-time Monitoring
            </p>
          </div>
          
          <div style={{ textAlign: 'right' }}>
            <div style={{
              backgroundColor: getConnectionStatusColor(),
              color: 'white',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '600',
              marginBottom: '8px'
            }}>
              {connectionStatus === 'CONNECTED' ? '🟢 Connected' : 
               connectionStatus === 'DISCONNECTED' ? '🔴 Disconnected' : '🟡 Connecting'}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              {new Date().toLocaleString('id-ID')}
            </div>
          </div>
        </div>

        {/* Gate selector untuk monitoring mode */}
        {gateConfig.isMonitoringAll() && (
          <div style={{ marginTop: '16px' }}>
            <GateSelector showSelector={true} />
          </div>
        )}
      </div>

      {/* Status Grid */}
      <div className="status-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '20px'
      }}>
        {/* Gate Status */}
        <div className="status-card" style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 16px 0' }}>🚪 Status Gate</h3>
          {gateStatus ? (
            <div>
              <div style={{ 
                padding: '8px 12px', 
                backgroundColor: gateStatus.status === 'online' ? '#E8F5E8' : '#FFEBEE',
                color: gateStatus.status === 'online' ? '#2E7D32' : '#C62828',
                borderRadius: '8px',
                marginBottom: '12px',
                fontWeight: '600'
              }}>
                {gateStatus.status === 'online' ? '✅ Online' : '❌ Offline'}
              </div>
              
              {gateStatus.controller_status && (
                <div style={{ fontSize: '12px', color: '#666' }}>
                  <div>📹 Camera: {gateStatus.controller_status.hardware?.camera?.connected ? '✅' : '❌'}</div>
                  <div>💳 Card Reader: {gateStatus.controller_status.hardware?.card_reader?.connected ? '✅' : '❌'}</div>
                  <div>🔧 Arduino: {gateStatus.controller_status.hardware?.arduino?.connected ? '✅' : '❌'}</div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ color: '#999' }}>Loading...</div>
          )}
        </div>

        {/* Parking Count */}
        <div className="status-card" style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 16px 0' }}>🚗 Kapasitas Parkir</h3>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2196F3' }}>
                {parkingCount.total}
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>Total</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#F44336' }}>
                {parkingCount.occupied}
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>Terisi</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4CAF50' }}>
                {parkingCount.available}
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>Tersedia</div>
            </div>
          </div>
        </div>

        {/* Quick Actions - hanya untuk gate-specific */}
        {gateConfig.isGateSpecific() && (
          <div className="status-card" style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ margin: '0 0 16px 0' }}>⚡ Quick Actions</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={() => handleManualGateControl('open')}
                style={{
                  backgroundColor: gateInfo.color,
                  color: 'white',
                  border: 'none',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                🔓 Buka Gate Manual
              </button>
              <button
                onClick={handleCaptureImage}
                style={{
                  backgroundColor: '#666',
                  color: 'white',
                  border: 'none',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                📸 Capture Image
              </button>
              <button
                onClick={simulateCardScan}
                style={{
                  backgroundColor: '#FF9800',
                  color: 'white',
                  border: 'none',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                🧪 Test Card Scan
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Recent Events */}
      <div className="recent-events" style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ margin: '0 0 16px 0' }}>
          📋 Recent Events {gateConfig.isGateSpecific() && `(${gateInfo.name})`}
        </h3>
        
        {recentEvents.length > 0 ? (
          <div className="events-list">
            {recentEvents.map((event) => (
              <div
                key={event.id}
                style={{
                  padding: '12px',
                  borderLeft: `4px solid ${event.type === 'entry' ? '#4CAF50' : '#F44336'}`,
                  backgroundColor: '#f9f9f9',
                  marginBottom: '8px',
                  borderRadius: '0 8px 8px 0'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span style={{ fontWeight: '600' }}>
                      {event.type === 'entry' ? '🚗➡️' : '🚗⬅️'} {event.message}
                    </span>
                    {event.gate && (
                      <span style={{ 
                        marginLeft: '8px', 
                        fontSize: '11px', 
                        backgroundColor: event.type === 'entry' ? '#4CAF50' : '#F44336',
                        color: 'white',
                        padding: '2px 6px',
                        borderRadius: '4px'
                      }}>
                        {event.gate.replace('gate_', '').toUpperCase()}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {formatTime(event.timestamp)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ 
            textAlign: 'center', 
            color: '#999', 
            padding: '40px',
            fontSize: '14px'
          }}>
            🕐 Belum ada aktivitas terbaru
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div style={{
        textAlign: 'center',
        marginTop: '20px',
        fontSize: '12px',
        color: '#999'
      }}>
        🖥️ Kiosk Mode - Monitor {gateInfo.name} • 
        Auto-refresh setiap 6 jam untuk stabilitas • 
        Sistem Parkir Manless v2.0
      </div>
    </div>
  )
}

export default GateSpecificDashboard 