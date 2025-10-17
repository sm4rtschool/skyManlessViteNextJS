// Smart WebSocket Service - Auto-detect channel from URL
// Otomatis connect ke WebSocket channel yang tepat berdasarkan route frontend

class SmartWebSocketService {
  constructor() {
    this.ws = null
    this.connected = false
    this.channel = null
    this.url = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectDelay = 2000
    this.shouldReconnect = true
    
    // Event listeners
    this.listeners = new Map()
    
    // Connection monitoring
    this.pingInterval = null
    this.lastPingTime = null
    
    // Auto-detect channel from URL
    this.detectChannelFromURL()
    
    console.log(`🧠 Smart WebSocket initialized for channel: ${this.channel}`)
  }

  detectChannelFromURL() {
    /**
     * Deteksi channel WebSocket berdasarkan URL frontend
     * /gate-in → gate_in
     * /gate-out → gate_out  
     * /admin → gate_all
     * /dashboard → gate_all
     * default → gate_all
     */
    const path = window.location.pathname.toLowerCase()
    
    if (path.includes('gate-in') || path.includes('gatein')) {
      this.channel = 'gate_in'
    } else if (path.includes('gate-out') || path.includes('gateout')) {
      this.channel = 'gate_out'
    } else if (path.includes('admin') || path.includes('dashboard') || path.includes('monitor')) {
      this.channel = 'gate_all'
    } else {
      // Default untuk route lain (bisa dikustomisasi)
      this.channel = 'gate_all'
    }
    
    this.url = `ws://localhost:8000/ws/${this.channel}`
    
    console.log(`🎯 Detected route: ${path} → Channel: ${this.channel}`)
  }

  connect() {
    if (this.connected) {
      console.log(`⚠️ Already connected to ${this.channel}`)
      return
    }

    console.log(`🔗 Smart connecting to ${this.url}...`)
    
    try {
      this.ws = new WebSocket(this.url)
      
      this.ws.onopen = (event) => {
        this.onOpen(event)
      }
      
      this.ws.onmessage = (event) => {
        this.onMessage(event)
      }
      
      this.ws.onclose = (event) => {
        this.onClose(event)
      }
      
      this.ws.onerror = (error) => {
        this.onError(error)
      }
      
    } catch (error) {
      console.error(`❌ Smart WebSocket connection failed:`, error)
      this.scheduleReconnect()
    }
  }

  onOpen(event) {
    console.log(`✅ Smart WebSocket connected to ${this.channel}`)
    this.connected = true
    this.reconnectAttempts = 0
    
    // Start ping monitoring
    this.startPingMonitoring()
    
    // Request initial data
    setTimeout(() => {
      this.requestInitialData()
    }, 500)
    
    this.emit('connected', { 
      channel: this.channel,
      url: this.url,
      timestamp: new Date().toISOString() 
    })
  }

  requestInitialData() {
    /**
     * Request data awal sesuai dengan channel
     */
    if (this.channel === 'gate_in' || this.channel === 'gate_out') {
      // Request status untuk gate spesifik
      this.send('request_status', { gate_id: this.channel })
    } else if (this.channel === 'gate_all') {
      // Request status semua gate untuk admin
      this.send('request_status', {})
    }
  }

  onMessage(event) {
    try {
      const data = JSON.parse(event.data)
      const { type, payload, gate_id, timestamp } = data
      
      console.log(`📨 [${this.channel}] ${type}:`, payload)
      
      // Filter data sesuai channel jika diperlukan
      if (this.shouldProcessMessage(type, data)) {
        // Emit event berdasarkan message type
        this.emit(type, { 
          payload, 
          gate_id, 
          timestamp,
          channel: this.channel 
        })
        
        // Emit event umum
        this.emit('message', data)
      }
      
    } catch (error) {
      console.error(`Error parsing message:`, error)
      console.log('Raw message:', event.data)
    }
  }

  shouldProcessMessage(type, data) {
    /**
     * Filter pesan berdasarkan channel
     * gate_in/gate_out: hanya data untuk gate tersebut
     * gate_all: semua data
     */
    if (this.channel === 'gate_all') {
      return true // Admin menerima semua data
    }
    
    // Untuk gate spesifik, hanya terima data untuk gate tersebut
    if (data.gate_id && data.gate_id !== this.channel) {
      console.log(`🚫 Filtered out message for ${data.gate_id} (current: ${this.channel})`)
      return false
    }
    
    return true
  }

  onClose(event) {
    console.log(`🔌 Smart WebSocket disconnected from ${this.channel}`)
    this.connected = false
    
    this.stopPingMonitoring()
    
    this.emit('disconnected', { 
      channel: this.channel,
      code: event.code,
      reason: event.reason,
      timestamp: new Date().toISOString() 
    })
    
    if (this.shouldReconnect) {
      this.scheduleReconnect()
    }
  }

  onError(error) {
    console.error(`❌ Smart WebSocket error:`, error)
    this.emit('error', { 
      error, 
      channel: this.channel,
      timestamp: new Date().toISOString() 
    })
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(`Max reconnect attempts reached for ${this.channel}`)
      return
    }
    
    this.reconnectAttempts++
    const delay = this.reconnectDelay * this.reconnectAttempts
    
    console.log(`🔄 Reconnecting to ${this.channel} in ${delay}ms (attempt ${this.reconnectAttempts})`)
    
    setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect()
      }
    }, delay)
  }

  startPingMonitoring() {
    this.pingInterval = setInterval(() => {
      if (this.connected) {
        this.ping()
      }
    }, 30000)
  }

  stopPingMonitoring() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  ping() {
    this.lastPingTime = Date.now()
    this.send('ping', { 
      timestamp: new Date().toISOString() 
    })
  }

  send(type, payload = {}) {
    if (!this.connected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn(`⚠️ Cannot send message: not connected to ${this.channel}`)
      return false
    }

    try {
      const message = {
        type,
        payload,
        timestamp: new Date().toISOString()
      }
      
      this.ws.send(JSON.stringify(message))
      console.log(`📤 [${this.channel}] ${type}:`, payload)
      return true
    } catch (error) {
      console.error(`Error sending message:`, error)
      return false
    }
  }

  // Event management
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, [])
    }
    this.listeners.get(eventType).push(callback)
    
    console.log(`📝 Registered listener for '${eventType}' on ${this.channel}`)
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
      const callbacks = this.listeners.get(eventType)
      callbacks.forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in event callback for ${eventType}:`, error)
        }
      })
    }
  }

  // Smart API Methods - otomatis sesuai channel
  openGate(duration = 10) {
    if (this.channel === 'gate_in' || this.channel === 'gate_out') {
      return this.send('gate_control', {
        action: 'open',
        gate_id: this.channel,
        duration
      })
    } else {
      console.warn('Gate control not available for admin channel')
      return false
    }
  }

  closeGate() {
    if (this.channel === 'gate_in' || this.channel === 'gate_out') {
      return this.send('gate_control', {
        action: 'close',
        gate_id: this.channel
      })
    } else {
      console.warn('Gate control not available for admin channel')
      return false
    }
  }

  captureImage() {
    if (this.channel === 'gate_in' || this.channel === 'gate_out') {
      return this.send('camera_control', {
        command: 'capture',
        gate_id: this.channel
      })
    } else {
      console.warn('Camera control not available for admin channel')
      return false
    }
  }

  requestStatus() {
    if (this.channel === 'gate_in' || this.channel === 'gate_out') {
      return this.send('request_status', { gate_id: this.channel })
    } else {
      return this.send('request_status', {}) // All gates for admin
    }
  }

  // Admin-specific methods
  controlSpecificGate(gateId, action, duration = 10) {
    if (this.channel === 'gate_all') {
      return this.send('gate_control', {
        action,
        gate_id: gateId,
        duration
      })
    } else {
      console.warn('Specific gate control only available for admin channel')
      return false
    }
  }

  // Connection management
  disconnect() {
    this.shouldReconnect = false
    this.connected = false
    
    this.stopPingMonitoring()
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    console.log(`🔌 Smart WebSocket manually disconnected from ${this.channel}`)
  }

  reconnect() {
    this.disconnect()
    this.shouldReconnect = true
    this.reconnectAttempts = 0
    
    // Re-detect channel in case URL changed
    this.detectChannelFromURL()
    
    setTimeout(() => {
      this.connect()
    }, 1000)
  }

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

  getCurrentChannel() {
    return this.channel
  }

  getCurrentURL() {
    return this.url
  }
}

// Create global instance
const smartWS = new SmartWebSocketService()

// React Hook untuk mudah digunakan
export const useSmartWebSocket = () => {
  return {
    connect: () => smartWS.connect(),
    disconnect: () => smartWS.disconnect(),
    reconnect: () => smartWS.reconnect(),
    isConnected: () => smartWS.isConnected(),
    getCurrentChannel: () => smartWS.getCurrentChannel(),
    
    // Event listeners
    on: (event, callback) => smartWS.on(event, callback),
    off: (event, callback) => smartWS.off(event, callback),
    
    // Actions
    openGate: (duration) => smartWS.openGate(duration),
    closeGate: () => smartWS.closeGate(),
    captureImage: () => smartWS.captureImage(),
    requestStatus: () => smartWS.requestStatus(),
    
    // Admin actions
    controlSpecificGate: (gateId, action, duration) => smartWS.controlSpecificGate(gateId, action, duration),
    
    // Raw send
    send: (type, payload) => smartWS.send(type, payload)
  }
}

// Direct exports
export const connectSmart = () => smartWS.connect()
export const disconnectSmart = () => smartWS.disconnect()
export const isConnectedSmart = () => smartWS.isConnected()
export const getCurrentChannelSmart = () => smartWS.getCurrentChannel()

// Export instance
export { smartWS }
export default smartWS

// Auto-connect when imported (optional)
if (typeof window !== 'undefined') {
  // Auto-connect after a small delay to allow app to initialize
  setTimeout(() => {
    console.log('🚀 Auto-connecting Smart WebSocket...')
    smartWS.connect()
  }, 1000)
} 