// WebSocket Service untuk real-time communication dengan Backend Central Hub
// Arsitektur Terpusat: Frontend ←→ Backend Central Hub (8000) ←→ Gate Controllers
// Support per-gate filtering untuk monitor kiosk mode

import { gateConfig } from './gateConfig.js'

class WebSocketService {
  constructor() {
    this.ws = null
    this.url = 'ws://localhost:8000/ws'  // Central Hub WebSocket
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectDelay = 2000
    this.listeners = new Map()
    this.connected = false
    this.shouldReconnect = true
    
    // Connection stability
    this.connectionCheckInterval = null
    this.lastPingTime = null
    this.pingInterval = 30000 // 30 seconds
    this.lastStatusRequest = null
  }

  connect() {
    if (this.connected) {
      console.log('⚠️ Already connected to Central Hub')
      return
    }

    console.log('🔗 Connecting to Central Hub WebSocket...')
    
    try {
      this.ws = new WebSocket(this.url)
      
      // Safe event binding with error handling
      this.ws.onopen = (event) => {
        try {
          this.onOpen(event)
        } catch (error) {
          console.error('Error in onOpen handler:', error)
        }
      }
      
      this.ws.onmessage = (event) => {
        try {
          this.onMessage(event)
        } catch (error) {
          console.error('Error in onMessage handler:', error)
        }
      }
      
      this.ws.onclose = (event) => {
        try {
          this.onClose(event)
        } catch (error) {
          console.error('Error in onClose handler:', error)
        }
      }
      
      this.ws.onerror = (error) => {
        try {
          this.onError(error)
        } catch (handlerError) {
          console.error('Error in onError handler:', handlerError)
          console.error('Original error:', error)
        }
      }
      
    } catch (error) {
      console.error('❌ Failed to create WebSocket connection:', error)
      this.scheduleReconnect()
    }
  }

  onOpen() {
    console.log('✅ Connected to Central Hub WebSocket')
    this.connected = true
    this.reconnectAttempts = 0
    
    // Start connection health monitoring
    this.startConnectionMonitoring()
    
    // Wait a bit for connection to stabilize before sending
    setTimeout(() => {
      if (this.connected && this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send('request_system_status', {})
      }
    }, 200) // Increased delay for better stability
    
    this.emit('connected', { timestamp: new Date().toISOString() })
  }

  startConnectionMonitoring() {
    // Clear existing interval
    if (this.connectionCheckInterval) {
      clearInterval(this.connectionCheckInterval)
    }
    
    // Start ping monitoring
    this.connectionCheckInterval = setInterval(() => {
      if (this.connected && this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.sendPing()
      }
    }, this.pingInterval)
  }

  sendPing() {
    this.lastPingTime = Date.now()
    this.send('ping', { timestamp: new Date().toISOString() })
  }

  stopConnectionMonitoring() {
    if (this.connectionCheckInterval) {
      clearInterval(this.connectionCheckInterval)
      this.connectionCheckInterval = null
    }
  }

  onMessage(event) {
    try {
      const data = JSON.parse(event.data)
      const { type, payload } = data
      
      // Handle ping/pong for connection health
      if (type === 'pong') {
        const latency = Date.now() - this.lastPingTime
        console.log(`🏓 Pong received - latency: ${latency}ms`)
        return
      }
      
      console.log('📨 Received from Central Hub:', type, payload)
      
      // Filter events berdasarkan gate configuration
      if (!this.shouldProcessMessage(type, payload)) {
        console.log('🚫 Message filtered out for current gate:', gateConfig.getCurrentGate())
        return
      }
      
      // Handle different message types
      switch (type) {
        case 'system_status':
          this.emit('system_status', payload)
          break
          
        case 'parking_event':
          this.handleParkingEvent(payload)
          break
          
        case 'parking_entry_result':
          this.emit('parking_entry_result', payload)
          break
          
        case 'parking_exit_result':
          this.emit('parking_exit_result', payload)
          break
          
        case 'gate_control_result':
          this.emit('gate_control_result', payload)
          break
          
        case 'parking_capacity':
          this.emit('parking_capacity', payload)
          break
          
        case 'emergency_event':
          this.handleEmergencyEvent(payload)
          break
          
        case 'system_logs':
          this.emit('system_logs', payload)
          break
          
        case 'hardware_status':
          this.emit('hardware_status', payload)
          break
          
        case 'image_captured':
          this.emit('image_captured', payload)
          break
          
        case 'camera_stream_url':
          this.emit('camera_stream_url', payload)
          break
          
        case 'force_exit_result':
          this.emit('force_exit_result', payload)
          break
          
        case 'error':
          console.error('❌ Central Hub error:', payload)
          this.emit('error', payload)
          break
          
        default:
          console.warn('Unknown message type:', type)
          this.emit('unknown_message', { type, payload })
      }
      
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }

  shouldProcessMessage(type, payload) {
    // Jika monitoring semua gate, terima semua message
    if (gateConfig.isMonitoringAll()) {
      return true
    }

    // Message types yang selalu diproses (system-wide)
    const alwaysProcessTypes = [
      'system_status',
      'parking_capacity', 
      'error',
      'connected',
      'disconnected'
    ]

    if (alwaysProcessTypes.includes(type)) {
      return true
    }

    // Filter message berdasarkan gate
    return gateConfig.shouldProcessEvent(payload)
  }

  handleParkingEvent(payload) {
    const { event, gate, result } = payload
    
    console.log(`🚗 Parking ${event} at ${gate}:`, result)
    
    // Emit specific event types
    this.emit('parking_event', payload)
    this.emit(`parking_${event}`, { gate, result })
    
    // Emit gate-specific events
    if (gate === 'gate_in') {
      this.emit('gate_in_event', { event, result })
    } else if (gate === 'gate_out') {
      this.emit('gate_out_event', { event, result })
    }
  }

  handleEmergencyEvent(payload) {
    const { event, result } = payload
    
    console.warn('🚨 Emergency event:', event, result)
    
    this.emit('emergency_event', payload)
    this.emit(`emergency_${event}`, result)
    
    // Show notification for emergency events
    if (window.Notification && Notification.permission === 'granted') {
      new Notification('🚨 Emergency Event', {
        body: `${event}: ${result.reason || 'Emergency action performed'}`,
        icon: '/favicon.ico'
      })
    }
  }

  onClose(event) {
    console.log('🔌 Central Hub WebSocket disconnected')
    this.connected = false
    
    // Stop connection monitoring
    this.stopConnectionMonitoring()
    
    this.emit('disconnected', { 
      code: event?.code || 1000, 
      reason: event?.reason || 'Connection closed',
      wasClean: event?.wasClean || false,
      timestamp: new Date().toISOString()
    })
    
    if (this.shouldReconnect) {
      this.scheduleReconnect()
    }
  }

  onError(error) {
    console.error('❌ Central Hub WebSocket error:', error)
    this.emit('error', { 
      error: error.message || error.toString() || 'Unknown WebSocket error',
      type: error.type || 'websocket_error',
      timestamp: new Date().toISOString()
    })
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('🔴 Max reconnection attempts reached')
      this.emit('max_reconnect_attempts')
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1), 30000) // Exponential backoff, max 30s
    console.log(`🔄 Reconnecting to Central Hub in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
    
    setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect()
      }
    }, delay)
  }

  send(type, payload = {}) {
    if (!this.connected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket not ready, cannot send message:', type, 'State:', this.getConnectionState())
      return false
    }

    try {
      const message = JSON.stringify({ type, payload })
      this.ws.send(message)
      console.log('📤 Sent to Central Hub:', type, payload)
      return true
    } catch (error) {
      console.error('Error sending WebSocket message:', error)
      return false
    }
  }

  // Parking Operations
  requestParkingEntry(cardId, licensePlate = null) {
    return this.send('parking_entry', {
      card_id: cardId,
      license_plate: licensePlate,
      timestamp: new Date().toISOString()
    })
  }

  requestParkingExit(cardId, paymentMethod = 'card') {
    return this.send('parking_exit', {
      card_id: cardId,
      payment_method: paymentMethod,
      timestamp: new Date().toISOString()
    })
  }

  // Gate Control
  controlGate(gateId, action, duration = 10) {
    return this.send('gate_control', {
      gate_id: gateId,
      action: action,
      duration: duration
    })
  }

  openGateIn(duration = 10) {
    return this.controlGate('gate_in', 'open', duration)
  }

  closeGateIn() {
    return this.controlGate('gate_in', 'close')
  }

  openGateOut(duration = 10) {
    return this.controlGate('gate_out', 'open', duration)
  }

  closeGateOut() {
    return this.controlGate('gate_out', 'close')
  }

  // Camera Control
  captureImage(gateId) {
    return this.send('camera_control', {
      gate_id: gateId,
      command: 'capture_image'
    })
  }

  getCameraStreamUrl(gateId) {
    return this.send('camera_control', {
      gate_id: gateId,
      command: 'get_stream_url'
    })
  }

  captureImageGateIn() {
    return this.captureImage('gate_in')
  }

  captureImageGateOut() {
    return this.captureImage('gate_out')
  }

  // System Operations
  requestSystemStatus() {
    // Throttle requests untuk mengurangi beban sistem
    if (this.lastStatusRequest && Date.now() - this.lastStatusRequest < 2000) {
      console.log('⚠️ System status request throttled')
      return
    }
    
    this.lastStatusRequest = Date.now()
    this.send('request_system_status', {
      timestamp: new Date().toISOString(),
      throttled: true
    })
  }

  requestParkingCapacity() {
    return this.send('request_parking_capacity', {})
  }

  requestLogs(gateId = null, limit = 50) {
    return this.send('request_logs', {
      gate_id: gateId,
      limit: limit
    })
  }

  requestLogsGateIn(limit = 50) {
    return this.requestLogs('gate_in', limit)
  }

  requestLogsGateOut(limit = 50) {
    return this.requestLogs('gate_out', limit)
  }

  requestAllLogs(limit = 100) {
    return this.requestLogs(null, limit)
  }

  // Emergency Operations
  forceExitSession(cardId, reason = 'manual') {
    return this.send('force_exit_session', {
      card_id: cardId,
      reason: reason
    })
  }

  // Event Listener Management
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, [])
    }
    this.listeners.get(eventType).push(callback)
  }

  off(eventType, callback) {
    if (this.listeners.has(eventType)) {
      const callbacks = this.listeners.get(eventType)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in event callback for ${eventType}:`, error)
        }
      })
    }
  }

  // Connection Management
  disconnect() {
    this.shouldReconnect = false
    
    // Stop connection monitoring
    this.stopConnectionMonitoring()
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.connected = false
    console.log('🔌 Manually disconnected from Central Hub')
  }

  reconnect() {
    this.disconnect()
    this.shouldReconnect = true
    this.reconnectAttempts = 0
    
    setTimeout(() => {
      this.connect()
    }, 1000)
  }

  // Utility Methods
  isConnected() {
    return this.connected && this.ws && this.ws.readyState === WebSocket.OPEN
  }

  getConnectionState() {
    if (!this.ws) return 'DISCONNECTED'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING'
      case WebSocket.OPEN: return 'CONNECTED'
      case WebSocket.CLOSING: return 'CLOSING'
      case WebSocket.CLOSED: return 'CLOSED'
      default: return 'UNKNOWN'
    }
  }

  // Simulation Methods (untuk development)
  simulateCardScan(gateId, cardId = 'TEST_CARD_001', licensePlate = null) {
    if (gateId === 'gate_in') {
      return this.requestParkingEntry(cardId, licensePlate)
    } else if (gateId === 'gate_out') {
      return this.requestParkingExit(cardId)
    }
  }

  simulateVehicleEntry(cardId = 'TEST_CARD_001', licensePlate = 'B1234XYZ') {
    return this.simulateCardScan('gate_in', cardId, licensePlate)
  }

  simulateVehicleExit(cardId = 'TEST_CARD_001') {
    return this.simulateCardScan('gate_out', cardId)
  }
}

// Export singleton instance
export const wsService = new WebSocketService()
export default wsService

// Auto-connect when imported
if (typeof window !== 'undefined') {
  // Request notification permission
  if (window.Notification && Notification.permission === 'default') {
    Notification.requestPermission()
  }
  
  // Don't auto-connect here to avoid duplicates
  // Let components handle connection explicitly
}

// Named exports for convenience
export const connectToHub = () => wsService.connect()
export const disconnectFromHub = () => wsService.disconnect()
export const isConnectedToHub = () => wsService.isConnected()
export const sendToHub = (type, payload) => wsService.send(type, payload)
export const onHubEvent = (eventType, callback) => wsService.on(eventType, callback)
export const offHubEvent = (eventType, callback) => wsService.off(eventType, callback) 