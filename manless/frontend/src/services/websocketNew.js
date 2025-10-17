// WebSocket Client untuk Frontend - Arsitektur Baru
// Frontend ←→ Backend WebSocket Server ←→ Controller

class WebSocketClient {
  constructor(channel = 'gate_all') {
    this.channel = channel
    this.url = `ws://localhost:8000/ws/${channel}`
    this.ws = null
    this.connected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectDelay = 2000
    this.shouldReconnect = true
    
    // Event listeners
    this.listeners = new Map()
    
    // Connection monitoring
    this.pingInterval = null
    this.lastPingTime = null
    
    console.log(`🔧 WebSocket Client initialized for channel: ${channel}`)
  }

  connect() {
    if (this.connected) {
      console.log(`⚠️ Already connected to channel ${this.channel}`)
      return
    }

    console.log(`🔗 Connecting to ${this.url}...`)
    
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
      console.error(`❌ Failed to create WebSocket connection to ${this.channel}:`, error)
      this.scheduleReconnect()
    }
  }

  onOpen(event) {
    console.log(`✅ Connected to channel ${this.channel}`)
    this.connected = true
    this.reconnectAttempts = 0
    
    // Start ping monitoring
    this.startPingMonitoring()
    
    // Request initial status
    setTimeout(() => {
      this.requestStatus()
    }, 500)
    
    this.emit('connected', { 
      channel: this.channel,
      timestamp: new Date().toISOString() 
    })
  }

  onMessage(event) {
    try {
      const data = JSON.parse(event.data)
      const { type, payload, gate_id, timestamp } = data
      
      console.log(`📨 [${this.channel}] Received:`, type, payload)
      
      // Emit event berdasarkan message type
      this.emit(type, { 
        payload, 
        gate_id, 
        timestamp,
        channel: this.channel 
      })
      
      // Emit event umum untuk semua pesan
      this.emit('message', data)
      
    } catch (error) {
      console.error(`Error parsing message from ${this.channel}:`, error)
      console.log('Raw message:', event.data)
    }
  }

  onClose(event) {
    console.log(`🔌 Disconnected from channel ${this.channel}`)
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
    console.error(`❌ WebSocket error on channel ${this.channel}:`, error)
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
    // Ping setiap 30 detik untuk menjaga koneksi
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
      console.warn(`⚠️ Cannot send message to ${this.channel}: not connected`)
      return false
    }

    try {
      const message = {
        type,
        payload,
        timestamp: new Date().toISOString()
      }
      
      this.ws.send(JSON.stringify(message))
      console.log(`📤 [${this.channel}] Sent:`, type, payload)
      return true
    } catch (error) {
      console.error(`Error sending message to ${this.channel}:`, error)
      return false
    }
  }

  // Event management
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, [])
    }
    this.listeners.get(eventType).push(callback)
    
    console.log(`📝 Registered listener for '${eventType}' on channel ${this.channel}`)
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

  // API Methods
  requestStatus(gateId = null) {
    return this.send('request_status', { gate_id: gateId })
  }

  controlGate(action, gateId = null, duration = 10) {
    return this.send('gate_control', {
      action,
      gate_id: gateId || this.getDefaultGateId(),
      duration
    })
  }

  controlCamera(command, gateId = null) {
    return this.send('camera_control', {
      command,
      gate_id: gateId || this.getDefaultGateId()
    })
  }

  requestParkingEntry(cardId, licensePlate = null) {
    return this.send('parking_entry', {
      card_id: cardId,
      license_plate: licensePlate
    })
  }

  requestParkingExit(cardId, paymentMethod = 'card') {
    return this.send('parking_exit', {
      card_id: cardId,
      payment_method: paymentMethod
    })
  }

  getDefaultGateId() {
    // Return gate ID based on channel
    if (this.channel === 'gate_in') return 'gate_in'
    if (this.channel === 'gate_out') return 'gate_out'
    return 'gate_in' // default
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
    
    console.log(`🔌 Manually disconnected from channel ${this.channel}`)
  }

  reconnect() {
    this.disconnect()
    this.shouldReconnect = true
    this.reconnectAttempts = 0
    
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
}

// WebSocket Manager untuk mengelola multiple channels
class WebSocketManager {
  constructor() {
    this.clients = new Map()
    this.defaultChannel = 'gate_all'
  }

  createClient(channel) {
    if (this.clients.has(channel)) {
      console.log(`Client for channel ${channel} already exists`)
      return this.clients.get(channel)
    }

    const client = new WebSocketClient(channel)
    this.clients.set(channel, client)
    
    console.log(`✅ Created WebSocket client for channel: ${channel}`)
    return client
  }

  getClient(channel = null) {
    const targetChannel = channel || this.defaultChannel
    
    if (!this.clients.has(targetChannel)) {
      return this.createClient(targetChannel)
    }
    
    return this.clients.get(targetChannel)
  }

  connectToChannel(channel) {
    const client = this.getClient(channel)
    client.connect()
    return client
  }

  disconnectFromChannel(channel) {
    if (this.clients.has(channel)) {
      const client = this.clients.get(channel)
      client.disconnect()
    }
  }

  disconnectAll() {
    for (const [channel, client] of this.clients) {
      client.disconnect()
    }
  }

  getConnectedChannels() {
    const connected = []
    for (const [channel, client] of this.clients) {
      if (client.isConnected()) {
        connected.push(channel)
      }
    }
    return connected
  }
}

// Create global manager instance
const wsManager = new WebSocketManager()

// Helper functions for easy usage
export const connectToGateIn = () => wsManager.connectToChannel('gate_in')
export const connectToGateOut = () => wsManager.connectToChannel('gate_out')
export const connectToGateAll = () => wsManager.connectToChannel('gate_all')
export const connectToAdmin = () => wsManager.connectToChannel('admin')

export const getGateInClient = () => wsManager.getClient('gate_in')
export const getGateOutClient = () => wsManager.getClient('gate_out')
export const getGateAllClient = () => wsManager.getClient('gate_all')
export const getAdminClient = () => wsManager.getClient('admin')

// Export main classes and manager
export { WebSocketClient, WebSocketManager, wsManager }

// Auto-connect to default channel when imported
if (typeof window !== 'undefined') {
  // Don't auto-connect to prevent confusion
  console.log('🔧 WebSocket service ready. Use connect functions to establish connections.')
} 