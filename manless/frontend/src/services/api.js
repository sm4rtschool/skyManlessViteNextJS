/**
 * API Service untuk komunikasi dengan Backend Central Hub
 * Arsitektur Terpusat: Frontend → Backend (8000) → Gate Controllers (8001, 8002)
 */

const API_BASE_URL = 'http://localhost:8000/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  // Helper method untuk HTTP requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout untuk mencegah hanging
      signal: AbortSignal.timeout(10000) // 10 second timeout
    }

    const config = { ...defaultOptions, ...options }

    try {
      console.log(`📡 API Request: ${endpoint}`)
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log(`✅ API Response: ${endpoint}`, data)
      return data
    } catch (error) {
      if (error.name === 'TimeoutError') {
        console.error(`⏰ API request timeout: ${endpoint}`)
        throw new Error(`Request timeout after 10 seconds: ${endpoint}`)
      } else if (error.name === 'AbortError') {
        console.error(`🚫 API request aborted: ${endpoint}`)
        throw new Error(`Request aborted: ${endpoint}`)
      } else {
        console.error(`❌ API request failed: ${endpoint}`, error)
        throw error
      }
    }
  }

  // System Status - CORRECT: menggunakan endpoint yang benar
  async getSystemStatus() {
    return this.request('/v1/system/status')  // Correct: /v1/system/status
  }

  // Parking Operations
  async parkingEntry(data) {
    return this.request('/v1/parking/entry', {  // Correct: /v1/parking/entry
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async parkingExit(data) {
    return this.request('/v1/parking/exit', {  // Correct: /v1/parking/exit
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // Parking Capacity - CORRECT: menggunakan endpoint yang benar
  async getParkingCapacity() {
    return this.request('/v1/system/stats')  // Correct: /v1/system/stats
  }

  // Gate Control - CORRECT: menggunakan endpoint yang benar
  async controlGate(gateId, action, duration = 10) {
    return this.request('/v1/gate/control', {  // Correct: /v1/gate/control
      method: 'POST',
      body: JSON.stringify({
        gate_id: gateId,
        action: action,
        duration: duration
      })
    })
  }

  // Gate IN specific
  async openGateIn(duration = 10) {
    return this.controlGate('gate_in', 'open', duration)
  }

  async closeGateIn() {
    return this.controlGate('gate_in', 'close')
  }

  // Gate OUT specific  
  async openGateOut(duration = 10) {
    return this.controlGate('gate_out', 'open', duration)
  }

  async closeGateOut() {
    return this.controlGate('gate_out', 'close')
  }

  // Camera Operations - CORRECT: menggunakan endpoint yang benar
  async getCameraStreamUrl(gateId) {
    return this.request('/camera/stream')  // Correct: /camera/stream
  }

  async captureImage(gateId) {
    return this.request('/camera/capture', {  // Correct: /camera/capture
      method: 'POST'
    })
  }

  // Capture images from both gates
  async captureImageGateIn() {
    return this.captureImage('gate_in')
  }

  async captureImageGateOut() {
    return this.captureImage('gate_out')
  }

  // System Logs - CORRECT: menggunakan endpoint yang benar
  async getLogs(gateId = null, limit = 50) {
    return this.request(`/v1/logs?limit=${limit}`)  // Correct: /v1/logs
  }

  // Logs by gate
  async getLogsGateIn(limit = 50) {
    return this.getLogs('gate_in', limit)
  }

  async getLogsGateOut(limit = 50) {
    return this.getLogs('gate_out', limit)
  }

  async getAllLogs(limit = 100) {
    return this.getLogs(null, limit)
  }

  // Emergency Operations - CORRECT: menggunakan endpoint yang benar
  async forceExitSession(cardId, reason = 'emergency') {
    return this.request('/v1/emergency/force-exit', {  // Correct: /v1/emergency/force-exit
      method: 'POST',
      body: JSON.stringify({
        card_id: cardId,
        reason: reason
      })
    })
  }

  // Simulation helpers (untuk development)
  async simulateCardScan(gateId, cardId, licensePlate = null) {
    if (gateId === 'gate_in') {
      return this.parkingEntry({
        card_id: cardId,
        license_plate: licensePlate
      })
    } else if (gateId === 'gate_out') {
      return this.parkingExit({
        card_id: cardId,
        license_plate: licensePlate,
        payment_method: 'card'
      })
    }
  }

  async simulateVehicleEntry(cardId = 'TEST_CARD_001', licensePlate = 'B1234XYZ') {
    return this.simulateCardScan('gate_in', cardId, licensePlate)
  }

  async simulateVehicleExit(cardId = 'TEST_CARD_001', paymentMethod = 'card') {
    return this.parkingExit({
      card_id: cardId,
      payment_method: paymentMethod
    })
  }

  // Health check individual gates (via central hub)
  async checkGateStatus(gateId) {
    const systemStatus = await this.getSystemStatus()
    
    if (systemStatus && systemStatus.gates && systemStatus.gates[gateId]) {
      return systemStatus.gates[gateId]
    }
    
    return null
  }

  async checkGateInStatus() {
    return this.checkGateStatus('gate_in')
  }

  async checkGateOutStatus() {
    return this.checkGateStatus('gate_out')
  }

  // Batch operations
  async getAllGatesStatus() {
    const systemStatus = await this.getSystemStatus()
    return {
      coordinator: systemStatus.coordinator,
      gates: systemStatus.gates,
      active_sessions: systemStatus.active_sessions
    }
  }

  async openAllGates(duration = 10) {
    const results = await Promise.allSettled([
      this.openGateIn(duration),
      this.openGateOut(duration)
    ])
    
    return {
      gate_in: results[0].status === 'fulfilled' ? results[0].value : results[0].reason,
      gate_out: results[1].status === 'fulfilled' ? results[1].value : results[1].reason
    }
  }

  async closeAllGates() {
    const results = await Promise.allSettled([
      this.closeGateIn(),
      this.closeGateOut()
    ])
    
    return {
      gate_in: results[0].status === 'fulfilled' ? results[0].value : results[0].reason,
      gate_out: results[1].status === 'fulfilled' ? results[1].value : results[1].reason
    }
  }

  async captureAllImages() {
    const results = await Promise.allSettled([
      this.captureImageGateIn(),
      this.captureImageGateOut()
    ])
    
    return {
      gate_in: results[0].status === 'fulfilled' ? results[0].value : results[0].reason,
      gate_out: results[1].status === 'fulfilled' ? results[1].value : results[1].reason
    }
  }
}

// Create singleton instance
const apiService = new ApiService()

// Export individual functions for convenience
export const getSystemStatus = () => apiService.getSystemStatus()
export const getParkingCapacity = () => apiService.getParkingCapacity()
export const checkGateStatus = (gateId) => apiService.checkGateStatus(gateId)
export const checkGateInStatus = () => apiService.checkGateInStatus()
export const checkGateOutStatus = () => apiService.checkGateOutStatus()
export const getAllGatesStatus = () => apiService.getAllGatesStatus()
export const openAllGates = (duration) => apiService.openAllGates(duration)
export const closeAllGates = () => apiService.closeAllGates()
export const captureAllImages = () => apiService.captureAllImages()
export const getLogs = (gateId, limit) => apiService.getLogs(gateId, limit)
export const getLogsGateIn = (limit) => apiService.getLogsGateIn(limit)
export const getLogsGateOut = (limit) => apiService.getLogsGateOut(limit)
export const getAllLogs = (limit) => apiService.getAllLogs(limit)
export const forceExitSession = (cardId, reason) => apiService.forceExitSession(cardId, reason)
export const simulateCardScan = (gateId, cardId, licensePlate) => apiService.simulateCardScan(gateId, cardId, licensePlate)
export const simulateVehicleEntry = (cardId, licensePlate) => apiService.simulateVehicleEntry(cardId, licensePlate)
export const simulateVehicleExit = (cardId, paymentMethod) => apiService.simulateVehicleExit(cardId, paymentMethod)
export const parkingEntry = (data) => apiService.parkingEntry(data)
export const parkingExit = (data) => apiService.parkingExit(data)

// Export the service instance for advanced usage
export { apiService } 