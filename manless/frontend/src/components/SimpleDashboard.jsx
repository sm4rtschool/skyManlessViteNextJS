import React, { useState, useEffect } from 'react'
import { gateConfig } from '../services/gateConfig.js'
import { wsService } from '../services/websocket.js'

const SimpleDashboard = () => {
  const [gateInfo, setGateInfo] = useState(gateConfig.getGateInfo())
  const [connectionStatus, setConnectionStatus] = useState('CONNECTING')
  const [systemStatus, setSystemStatus] = useState(null)
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    // Update time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    // WebSocket connection
    const handleConnected = () => {
      console.log('✅ WebSocket Connected')
      setConnectionStatus('CONNECTED')
    }

    const handleDisconnected = () => {
      console.log('❌ WebSocket Disconnected')
      setConnectionStatus('DISCONNECTED')
    }

    const handleSystemStatus = (data) => {
      console.log('📊 System Status:', data)
      setSystemStatus(data)
    }

    // Subscribe to WebSocket events
    wsService.on('connected', handleConnected)
    wsService.on('disconnected', handleDisconnected)
    wsService.on('system_status', handleSystemStatus)

    // Request initial status
    wsService.requestSystemStatus()

    return () => {
      wsService.off('connected', handleConnected)
      wsService.off('disconnected', handleDisconnected)
      wsService.off('system_status', handleSystemStatus)
      clearInterval(timeInterval)
    }
  }, [])

  const simulateCardScan = () => {
    const cardId = `TEST_${Date.now()}`
    console.log(`🔍 Simulating card scan: ${cardId}`)
    wsService.simulateCardScan(gateConfig.getCurrentGate(), cardId, 'B1234XYZ')
  }

  const openGate = () => {
    console.log('🚪 Opening gate...')
    wsService.controlGate(gateConfig.getCurrentGate(), 'open', 10)
  }

  const captureImage = () => {
    console.log('📸 Capturing image...')
    wsService.captureImage(gateConfig.getCurrentGate())
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{
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
              📍 {gateInfo.location} • 🔗 Simple Dashboard
            </p>
          </div>
          
          <div style={{ textAlign: 'right' }}>
            <div style={{
              backgroundColor: connectionStatus === 'CONNECTED' ? '#4CAF50' : '#F44336',
              color: 'white',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '600',
              marginBottom: '8px'
            }}>
              {connectionStatus === 'CONNECTED' ? '🟢 Connected' : '🔴 Disconnected'}
            </div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              {currentTime.toLocaleString('id-ID')}
            </div>
          </div>
        </div>
      </div>

      {/* Status Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '20px',
        marginBottom: '20px'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#333' }}>🔗 Connection Status</h3>
          <p style={{ margin: 0, color: connectionStatus === 'CONNECTED' ? '#4CAF50' : '#F44336' }}>
            {connectionStatus}
          </p>
        </div>

        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#333' }}>📊 System Status</h3>
          <p style={{ margin: 0, color: '#666' }}>
            {systemStatus ? 'Online' : 'Loading...'}
          </p>
        </div>

        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#333' }}>🚗 Active Sessions</h3>
          <p style={{ margin: 0, color: '#666' }}>
            {systemStatus?.coordinator?.active_sessions || 0}
          </p>
        </div>

        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#333' }}>⏰ Current Time</h3>
          <p style={{ margin: 0, color: '#666' }}>
            {currentTime.toLocaleTimeString('id-ID')}
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>🎮 Quick Actions</h3>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={simulateCardScan}
            style={{
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            🔍 Simulate Card Scan
          </button>
          
          <button
            onClick={openGate}
            style={{
              backgroundColor: '#16a34a',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            🚪 Open Gate
          </button>
          
          <button
            onClick={captureImage}
            style={{
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            📸 Capture Image
          </button>
        </div>
      </div>

      {/* System Status Details */}
      {systemStatus && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '20px',
          marginTop: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>📋 System Details</h3>
          <pre style={{
            backgroundColor: '#f9fafb',
            padding: '16px',
            borderRadius: '8px',
            fontSize: '12px',
            color: '#374151',
            overflow: 'auto',
            maxHeight: '200px'
          }}>
            {JSON.stringify(systemStatus, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default SimpleDashboard 