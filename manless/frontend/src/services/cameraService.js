/**
 * Camera Service untuk streaming melalui Controller
 * Menggunakan WebSocket khusus untuk camera streaming
 */

class CameraService {
  constructor() {
    this.ws = null
    this.isStreaming = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
    this.frameListeners = []
    this.statusListeners = []
  }

  connect() {
    if (this.ws) {
      this.disconnect()
    }

    try {
      // Connect ke camera WebSocket endpoint di controller
      this.ws = new WebSocket('ws://localhost:8001/ws/camera')
      
      this.ws.onopen = () => {
        console.log('Camera WebSocket connected')
        this.isStreaming = true
        this.reconnectAttempts = 0
        this.notifyStatusListeners({ connected: true, streaming: true })
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('Error parsing camera WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('Camera WebSocket disconnected')
        this.isStreaming = false
        this.notifyStatusListeners({ connected: false, streaming: false })
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('Camera WebSocket error:', error)
        this.notifyStatusListeners({ connected: false, streaming: false, error: true })
      }

    } catch (error) {
      console.error('Failed to connect Camera WebSocket:', error)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.isStreaming = false
  }

  scheduleReconnect() {
    this.reconnectAttempts++
    console.log(`Reconnecting camera in ${this.reconnectInterval}ms (attempt ${this.reconnectAttempts})`)
    
    setTimeout(() => {
      this.connect()
    }, this.reconnectInterval)
  }

  handleMessage(data) {
    const { type, payload } = data
    
    switch (type) {
      case 'camera_frame':
        this.notifyFrameListeners(payload)
        break
      case 'camera_info':
        this.notifyStatusListeners({ ...payload, connected: true })
        break
      case 'error':
        console.error('Camera error:', payload)
        this.notifyStatusListeners({ connected: false, error: payload })
        break
      default:
        console.log('Unknown camera message type:', type)
    }
  }

  // Frame listeners management
  onFrame(callback) {
    this.frameListeners.push(callback)
    
    // Return unsubscribe function
    return () => {
      const index = this.frameListeners.indexOf(callback)
      if (index > -1) {
        this.frameListeners.splice(index, 1)
      }
    }
  }

  // Status listeners management
  onStatus(callback) {
    this.statusListeners.push(callback)
    
    // Return unsubscribe function
    return () => {
      const index = this.statusListeners.indexOf(callback)
      if (index > -1) {
        this.statusListeners.splice(index, 1)
      }
    }
  }

  notifyFrameListeners(frameData) {
    this.frameListeners.forEach(callback => {
      try {
        callback(frameData)
      } catch (error) {
        console.error('Error in frame listener:', error)
      }
    })
  }

  notifyStatusListeners(statusData) {
    this.statusListeners.forEach(callback => {
      try {
        callback(statusData)
      } catch (error) {
        console.error('Error in status listener:', error)
      }
    })
  }

  // Utility methods
  getConnectionStatus() {
    return this.isStreaming
  }

  getStreamUrl() {
    // HTTP stream endpoint sebagai fallback
    return 'http://localhost:8001/api/camera/stream'
  }

  // Auto-connect when service is created
  startStreaming() {
    if (!this.isStreaming) {
      this.connect()
    }
  }

  stopStreaming() {
    this.disconnect()
  }
}

// Singleton instance
const cameraService = new CameraService()

export default cameraService

// Named exports for convenience
export const connectCamera = () => cameraService.connect()
export const disconnectCamera = () => cameraService.disconnect()
export const onCameraFrame = (callback) => cameraService.onFrame(callback)
export const onCameraStatus = (callback) => cameraService.onStatus(callback)
export const getCameraStreamUrl = () => cameraService.getStreamUrl()
export const startCameraStreaming = () => cameraService.startStreaming()
export const stopCameraStreaming = () => cameraService.stopStreaming() 