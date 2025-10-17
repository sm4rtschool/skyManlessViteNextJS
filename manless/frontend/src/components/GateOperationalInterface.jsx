import React, { useState, useEffect, useRef } from 'react'
import { gateConfig } from '../services/gateConfig.js'
import { wsService } from '../services/websocket.js'
import { apiService } from '../services/api.js'
import LiveView from './LiveView.jsx'

// Global variable untuk prevent duplicate WebSocket logs
let globalConnectionLogged = false

const GateOperationalInterface = () => {
  const gateInfo = gateConfig.getGateInfo()
  const [currentTime, setCurrentTime] = useState(new Date())
  
  // Connection Status
  const [connectionStatus, setConnectionStatus] = useState({
    websocket: false,
    arduino: true,  // Set true untuk sementara
    camera: true,   // Set true untuk webcam mode
    cardReader: true  // Set true untuk sementara
  })
  
  // Gate Status
  const [gateStatus, setGateStatus] = useState({
    position: 'CLOSED',
    vehicleDetected: false,
    operationTime: null
  })
  
  // Card Reader Status
  const [cardReaderStatus, setCardReaderStatus] = useState({
    status: 'WAITING', // WAITING, DETECTED, VALID, INVALID
    cardId: null,
    lastRead: null
  })
  
  // Camera & Stream - SIMPLIFIED (IP Camera disabled untuk sementara)
  const [cameraConnected, setCameraConnected] = useState(true) // Set true untuk sementara (webcam laptop)
  const [cameraError, setCameraError] = useState(false)
  const [lastCapture, setLastCapture] = useState(new Date())
  
  // Parking Info
  const [parkingInfo, setParkingInfo] = useState({
    totalSlots: 100,
    occupied: 0,
    available: 100
  })
  
  // Real-time Logs
  const [logs, setLogs] = useState([])
  const logsRef = useRef(null)
  const maxLogs = 50

  // DISABLED: Dahua Camera Configuration (disabled untuk sementara)
  // const DAHUA_IP = '10.5.50.129'
  // const DAHUA_USERNAME = 'admin'
  // const DAHUA_PASSWORD = 'SKYUPH@2025'
  // const DAHUA_SNAPSHOT_URL = `http://${DAHUA_USERNAME}:${DAHUA_PASSWORD}@${DAHUA_IP}/cgi-bin/snapshot.cgi`
  
  // Initialize and setup connections
  useEffect(() => {
    // Reset global flag saat component baru mount
    console.log('🔄 Component mounted, resetting global flag')
    globalConnectionLogged = false
    
    // Setup WebSocket listeners
    wsService.on('connected', handleWebSocketConnected)
    wsService.on('disconnected', handleWebSocketDisconnected)
    wsService.on('system_status', handleSystemStatus)
    wsService.on('parking_capacity', handleParkingCapacity)
    wsService.on('card_event', handleCardEvent)
    wsService.on('gate_event', handleGateEvent)
    wsService.on('vehicle_event', handleVehicleEvent)
    wsService.on('camera_event', handleCameraEvent)
    wsService.on('ticket_event', handleTicketEvent)
    wsService.on('arduino_event', handleArduinoEvent)
    
    // Setup time updater
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    
    // DISABLED: Camera snapshot auto-refresh (disabled untuk sementara)
    // const snapshotInterval = setInterval(() => {
    //   setSnapshotKey(Date.now())
    // }, 3000)
    
    // Check current connection status
    const currentlyConnected = wsService.isConnected()
    
    if (!currentlyConnected) {
      // Connect if not connected
      wsService.connect()
    } else {
      // If already connected, update status and log once
      setConnectionStatus(prev => ({ ...prev, websocket: true }))
      console.log('🔍 Already connected, status updated')
      
      // Fallback log jika belum pernah log sama sekali
      if (!globalConnectionLogged) {
        addLog('WebSocket', 'Sudah terhubung ke Central Hub', 'success')
        globalConnectionLogged = true
        console.log('✅ Fallback log added for existing connection')
      }
    }
    
    // Request initial status after a short delay
    const requestInitialData = () => {
      if (wsService.isConnected()) {
        wsService.requestSystemStatus()
        wsService.requestParkingCapacity()
      } else {
        // Retry after 500ms if not connected yet
        setTimeout(requestInitialData, 500)
      }
    }
    
    setTimeout(requestInitialData, 500)
    
    return () => {
      clearInterval(timeInterval)
      // clearInterval(snapshotInterval) // DISABLED
      // Remove listeners
      wsService.off('connected', handleWebSocketConnected)
      wsService.off('disconnected', handleWebSocketDisconnected)
      wsService.off('system_status', handleSystemStatus)
      wsService.off('parking_capacity', handleParkingCapacity)
      wsService.off('card_event', handleCardEvent)
      wsService.off('gate_event', handleGateEvent)
      wsService.off('vehicle_event', handleVehicleEvent)
      wsService.off('camera_event', handleCameraEvent)
      wsService.off('ticket_event', handleTicketEvent)
      wsService.off('arduino_event', handleArduinoEvent)
    }
  }, [])

  // Auto-scroll logs to bottom
  useEffect(() => {
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight
    }
  }, [logs])

  // DISABLED: Auto refresh camera snapshot (untuk sementara)
  // useEffect(() => {
  //   const refreshCamera = () => {
  //     if (!cameraError) {
  //       const timestamp = Date.now()
  //       setSnapshotUrl(`${DAHUA_SNAPSHOT_URL}?t=${timestamp}`)
  //     }
  //   }
  //   refreshCamera()
  //   const cameraInterval = setInterval(refreshCamera, 2000)
  //   return () => {
  //     clearInterval(cameraInterval)
  //   }
  // }, [cameraError, DAHUA_SNAPSHOT_URL])

  const loadParkingInfo = async () => {
    try {
      const capacity = await apiService.getParkingCapacity()
      setParkingInfo({
        totalSlots: capacity.total || 100,
        occupied: capacity.occupied || 0,
        available: capacity.available || 100
      })
    } catch (error) {
      console.error('Error loading parking info:', error)
    }
  }

  const addLog = (component, message, type = 'info') => {
    try {
      const newLog = {
        id: Date.now() + Math.random(), // Ensure unique ID
        timestamp: new Date(),
        component: component || 'System',
        message: message || 'No message',
        type: type || 'info'
      }
      
      setLogs(prev => {
        try {
          const updated = [newLog, ...prev].slice(0, maxLogs)
          return updated
        } catch (error) {
          console.error('Error updating logs:', error)
          return prev
        }
      })
      
      // Auto scroll to top
      setTimeout(() => {
        try {
          if (logsRef.current) {
            logsRef.current.scrollTop = 0
          }
        } catch (error) {
          console.error('Error scrolling logs:', error)
        }
      }, 100)
    } catch (error) {
      console.error('Error adding log:', error)
    }
  }

  const getConnectionColor = (connected) => {
    return connected ? 'text-green-400' : 'text-red-400'
  }

  const getConnectionIcon = (connected) => {
    return connected ? '●' : '○'
  }

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-400'
      case 'warning': return 'text-yellow-400'
      case 'error': return 'text-red-400'
      default: return 'text-blue-400'
    }
  }

  // Event Handlers
  const handleWebSocketConnected = (data) => {
    try {
      console.log('🔍 handleWebSocketConnected triggered, globalConnectionLogged:', globalConnectionLogged)
      setConnectionStatus(prev => ({ ...prev, websocket: true }))
      
      // Use global flag untuk prevent duplicate logs dalam satu session
      if (!globalConnectionLogged) {
        addLog('WebSocket', 'Koneksi WebSocket berhasil', 'success')
        globalConnectionLogged = true
        console.log('✅ WebSocket connection log added')
      } else {
        console.log('⚠️ WebSocket connection already logged, skipping duplicate')
      }
    } catch (error) {
      console.error('Error handling WebSocket connected event:', error)
    }
  }
  
  const handleWebSocketDisconnected = (data) => {
    try {
      setConnectionStatus(prev => ({ ...prev, websocket: false }))
      const reason = data?.reason || 'Unknown reason'
      const code = data?.code || 'Unknown code'
      addLog('WebSocket', `Koneksi terputus (${code})`, 'error')
      
      // Reset global flag untuk reconnection berikutnya
      globalConnectionLogged = false
      console.log('🔄 Global connection flag reset for next connection')
    } catch (error) {
      console.error('Error handling WebSocket disconnected event:', error)
    }
  }
  
  const handleSystemStatus = (data) => {
    try {
      const currentGate = gateConfig.getCurrentGate()
      if (data?.gates && data.gates[currentGate]) {
        const gateData = data.gates[currentGate]
        setConnectionStatus(prev => ({
          ...prev,
          arduino: gateData.arduino?.connected || false,
          camera: gateData.camera?.connected || false,
          cardReader: gateData.card_reader?.connected || false
        }))
      }
    } catch (error) {
      console.error('Error handling system status:', error)
    }
  }
  
  const handleParkingCapacity = (data) => {
    try {
      setParkingInfo({
        totalSlots: data?.total_slots || 100,
        occupied: data?.occupied || 0,
        available: data?.available || 100
      })
    } catch (error) {
      console.error('Error handling parking capacity:', error)
    }
  }
  
  const handleCardEvent = (data) => {
    try {
      const { card_id, status, timestamp } = data || {}
      
      if (!card_id || !status) {
        console.warn('Invalid card event data:', data)
        return
      }
      
      setCardReaderStatus({
        status: status.toUpperCase(),
        cardId: card_id,
        lastRead: timestamp ? new Date(timestamp) : new Date()
      })
      
      const statusText = status === 'valid' ? 'VALID' : status === 'invalid' ? 'INVALID' : 'DETECTED'
      addLog('Card Reader', `Kartu ${card_id} - ${statusText}`, status === 'valid' ? 'success' : 'warning')
      
      // Auto reset after 5 seconds
      setTimeout(() => {
        setCardReaderStatus(prev => ({
          ...prev,
          status: 'WAITING',
          cardId: null
        }))
      }, 5000)
    } catch (error) {
      console.error('Error handling card event:', error)
    }
  }
  
  const handleGateEvent = (data) => {
    const { action, result, timestamp } = data
    setGateStatus(prev => ({
      ...prev,
      position: result.position || prev.position,
      operationTime: new Date(timestamp)
    }))
    
    addLog('Gate Control', `Gate ${action} - ${result.position}`, 'info')
  }
  
  const handleVehicleEvent = (data) => {
    const { event, detected, timestamp } = data
    setGateStatus(prev => ({
      ...prev,
      vehicleDetected: detected
    }))
    
    addLog('Vehicle Sensor', `Kendaraan ${detected ? 'terdeteksi' : 'tidak terdeteksi'}`, detected ? 'success' : 'info')
  }
  
  const handleCameraEvent = (data) => {
    const { event, result, timestamp } = data
    if (event === 'capture') {
      setLastCapture(new Date(timestamp))
      addLog('Camera', `Foto berhasil diambil: ${result.filename}`, 'success')
    } else if (event === 'stream_url') {
      setCameraStream(result.url)
    }
  }
  
  const handleTicketEvent = (data) => {
    const { event, result, timestamp } = data
    addLog('Ticket System', `Tiket ${event}: ${result.ticket_id}`, 'success')
  }
  
  const handleArduinoEvent = (data) => {
    const { command, result, timestamp } = data
    addLog('Arduino', `Command: ${command} - ${result.status}`, result.success ? 'success' : 'error')
  }

  return (
    <div className="min-h-screen bg-gray-900 text-green-400 font-mono">
      {/* Header */}
      <div className={`${gateInfo.location === 'gate_in' ? 'bg-green-800' : 'bg-red-800'} p-4 text-center`}>
        <h1 className="text-2xl font-bold text-white">
          {gateInfo.location === 'gate_in' ? '🚪➡️ Gate Masuk' : '🚪⬅️ Gate Keluar'} - Interface Operasional
        </h1>
        <p className="text-gray-200 mt-1">
          {gateInfo.description} | {currentTime.toLocaleDateString('id-ID', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4">
        {/* Left Column - Camera & Status */}
        <div className="space-y-4">
          {/* Live Camera View */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 text-white">📹 Live Camera View - Webcam Mode</h3>
            <div className="bg-black rounded-lg overflow-hidden mb-3" style={{ height: '300px' }}>
              <LiveView variant="dark" showCard={false} className="w-full h-full" />
            </div>
            <div className="text-sm space-y-1">
              <div className={`${getConnectionColor(cameraConnected && !cameraError)}`}>
                {getConnectionIcon(cameraConnected && !cameraError)} Camera: {cameraConnected && !cameraError ? 'CONNECTED' : 'DISCONNECTED'}
              </div>
              <div className="text-gray-400">
                Source: Webcam (IP Camera DISABLED)
              </div>
              <div className="text-gray-400">
                Mode: Live Webcam View
              </div>
              {lastCapture && (
                <div className="text-gray-400">
                  Last Update: {lastCapture.toLocaleTimeString('id-ID')}
                </div>
              )}
              <div className="text-gray-400">
                Status: Active Webcam Mode
              </div>
            </div>
          </div>

          {/* Connection Status */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 text-white">🔗 Status Koneksi</h3>
            <div className="space-y-2 text-sm">
              <div className={`${getConnectionColor(connectionStatus.websocket)}`}>
                {getConnectionIcon(connectionStatus.websocket)} WebSocket: {connectionStatus.websocket ? 'CONNECTED' : 'DISCONNECTED'}
              </div>
              <div className={`${getConnectionColor(connectionStatus.arduino)}`}>
                {getConnectionIcon(connectionStatus.arduino)} Arduino: {connectionStatus.arduino ? 'CONNECTED' : 'DISCONNECTED'}
              </div>
              <div className={`${getConnectionColor(connectionStatus.camera)}`}>
                {getConnectionIcon(connectionStatus.camera)} Camera: {connectionStatus.camera ? 'CONNECTED' : 'DISCONNECTED'}
              </div>
              <div className={`${getConnectionColor(connectionStatus.cardReader)}`}>
                {getConnectionIcon(connectionStatus.cardReader)} Card Reader: {connectionStatus.cardReader ? 'CONNECTED' : 'DISCONNECTED'}
              </div>
            </div>
          </div>
        </div>

        {/* Center Column - Card Reader & Gate Control */}
        <div className="space-y-4">
          {/* Card Reader Interface */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 text-white">💳 Card Reader Interface</h3>
            <div className="text-center">
              <div className={`text-3xl font-bold mb-2 ${
                cardReaderStatus.status === 'VALID' ? 'text-green-400' : 
                cardReaderStatus.status === 'INVALID' ? 'text-red-400' : 
                'text-yellow-400'
              }`}>
                {cardReaderStatus.status}
              </div>
              {cardReaderStatus.cardId && (
                <div className="text-lg text-white mb-2">
                  Card ID: {cardReaderStatus.cardId}
                </div>
              )}
              {cardReaderStatus.lastRead && (
                <div className="text-sm text-gray-400">
                  Last Read: {cardReaderStatus.lastRead.toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>

          {/* Gate Control Status */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 text-white">🚪 Gate Control Status</h3>
            <div className="space-y-3">
              <div className="text-center">
                <div className={`text-2xl font-bold ${
                  gateStatus.position === 'TERBUKA' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {gateStatus.position}
                </div>
              </div>
              {gateStatus.operationTime && (
                <div className="text-sm text-gray-400 text-center">
                  Last Operation: {gateStatus.operationTime.toLocaleTimeString()}
                </div>
              )}
              <div className={`text-center ${gateStatus.vehicleDetected ? 'text-green-400' : 'text-gray-500'}`}>
                🚗 Vehicle: {gateStatus.vehicleDetected ? 'DETECTED' : 'NOT DETECTED'}
              </div>
            </div>
          </div>

          {/* Parking Area Info */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 text-white">🅿️ Parking Area Info</h3>
            <div className="grid grid-cols-3 gap-2 text-center text-sm">
              <div>
                <div className="text-blue-400 font-bold text-lg">{parkingInfo.totalSlots}</div>
                <div className="text-gray-400">Total</div>
              </div>
              <div>
                <div className="text-red-400 font-bold text-lg">{parkingInfo.occupied}</div>
                <div className="text-gray-400">Occupied</div>
              </div>
              <div>
                <div className="text-green-400 font-bold text-lg">{parkingInfo.available}</div>
                <div className="text-gray-400">Available</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Time & Logs */}
        <div className="space-y-4">
          {/* Real-time Clock */}
          <div className="bg-gray-800 rounded-lg p-4 text-center">
            <h3 className="text-lg font-semibold mb-3 text-white">🕐 Real-time Clock</h3>
            <div className="text-3xl font-bold text-green-400 mb-2">
              {currentTime.toLocaleTimeString()}
            </div>
            <div className="text-sm text-gray-400">
              {currentTime.toLocaleDateString('id-ID', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
          </div>

          {/* Operational Logs */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 text-white">📋 Operational Logs</h3>
            <div 
              ref={logsRef}
              className="h-96 overflow-y-auto space-y-1 text-xs"
            >
              {logs.length === 0 ? (
                <div className="text-gray-500 text-center py-8">
                  No logs yet...
                </div>
              ) : (
                logs.map(log => (
                  <div key={log.id} className="border-b border-gray-700 pb-1">
                    <div className="flex justify-between items-start">
                      <span className={`font-semibold ${getLogColor(log.type)}`}>
                        {log.component}
                      </span>
                      <span className="text-gray-500">
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-gray-300 mt-1">
                      {log.message}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GateOperationalInterface 