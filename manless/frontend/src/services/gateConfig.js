// Gate Configuration Service
// Untuk mengatur frontend per gate (gate_in, gate_out, atau all)

class GateConfigService {
  constructor() {
    try {
      // Initialize gateInfo first
      this.gateInfo = {
        'gate_in': {
          id: 'gate_in',
          name: 'Gate Masuk',
          type: 'entry',
          location: 'Pintu Masuk Utama',
          color: '#4CAF50',
          icon: '🚪➡️',
          port: 8001
        },
        'gate_out': {
          id: 'gate_out', 
          name: 'Gate Keluar',
          type: 'exit',
          location: 'Pintu Keluar Utama',
          color: '#F44336',
          icon: '🚪⬅️',
          port: 8002
        },
        'all': {
          id: 'all',
          name: 'Semua Gate',
          type: 'monitoring',
          location: 'Control Center',
          color: '#2196F3',
          icon: '🏢',
          port: null
        }
      }
      
      // Then detect current gate
      const urlGate = this.detectGateFromURL()
      const storedGate = this.getStoredGate()
      
      // Prioritas: URL parameter > localStorage > default
      if (urlGate) {
        this.currentGate = urlGate
        // Clear localStorage jika ada parameter URL yang valid
        if (storedGate && storedGate !== urlGate) {
          console.log(`🔄 Clearing localStorage gate (${storedGate}) karena ada parameter URL (${urlGate})`)
          localStorage.removeItem('selected_gate')
        }
      } else if (storedGate) {
        this.currentGate = storedGate
      } else {
        this.currentGate = 'all'
      }
      
      console.log(`✅ GateConfig initialized: ${this.currentGate}`)
    } catch (error) {
      console.error('Error initializing GateConfig:', error)
      // Fallback values
      this.currentGate = 'all'
      this.gateInfo = {}
    }
  }

  // Deteksi gate dari URL parameter
  detectGateFromURL() {
    try {
      const urlParams = new URLSearchParams(window.location.search)
      const gateParam = urlParams.get('gate')
      
      console.log(`🔍 Detecting gate from URL parameter: ${gateParam}`)
      
      // Validate gate parameter
      if (gateParam && this.gateInfo && this.gateInfo[gateParam]) {
        console.log(`🚪 Gate detected from URL: ${gateParam}`)
        return gateParam
      }
      
      // Handle special case untuk gate_all (alias untuk 'all')
      if (gateParam === 'gate_all' || gateParam === 'all') {
        console.log(`🚪 Gate ALL detected from URL: ${gateParam}`)
        return 'all'
      }
      
      // Deteksi dari subdomain atau path (hanya jika tidak ada parameter gate yang valid)
      const hostname = window.location.hostname
      const pathname = window.location.pathname
      
      if (hostname.includes('gate-in') || pathname.includes('/gate-in')) {
        console.log('🚪 Gate IN detected from hostname/path')
        return 'gate_in'
      }
      
      if (hostname.includes('gate-out') || pathname.includes('/gate-out')) {
        console.log('🚪 Gate OUT detected from hostname/path')
        return 'gate_out'
      }
      
      console.log('❌ No valid gate detected from URL')
      return null
    } catch (error) {
      console.error('Error detecting gate from URL:', error)
      return null
    }
  }

  // Get stored gate dari localStorage
  getStoredGate() {
    try {
      const stored = localStorage.getItem('selected_gate')
      console.log(`📦 Stored gate from localStorage: ${stored}`)
      return stored
    } catch (error) {
      console.warn('Error accessing localStorage:', error)
      return null
    }
  }

  // Clear stored gate dari localStorage
  clearStoredGate() {
    try {
      localStorage.removeItem('selected_gate')
      console.log('🗑️ Cleared stored gate from localStorage')
    } catch (error) {
      console.warn('Error clearing localStorage:', error)
    }
  }

  // Set current gate
  setCurrentGate(gateId) {
    if (!this.gateInfo || !this.gateInfo[gateId]) {
      console.error(`❌ Invalid gate ID: ${gateId}`)
      return false
    }

    this.currentGate = gateId
    localStorage.setItem('selected_gate', gateId)
    
    // Update URL parameter tanpa reload
    const url = new URL(window.location)
    url.searchParams.set('gate', gateId)
    window.history.replaceState({}, '', url)
    
    console.log(`✅ Gate set to: ${this.getGateInfo().name}`)
    
    // Trigger event untuk update komponen
    window.dispatchEvent(new CustomEvent('gateChanged', { 
      detail: { gateId, gateInfo: this.getGateInfo() }
    }))
    
    return true
  }

  // Get current gate ID
  getCurrentGate() {
    return this.currentGate
  }

  // Get current gate info
  getGateInfo(gateId = null) {
    const gate = gateId || this.currentGate
    
    // Safety check
    if (!this.gateInfo) {
      console.warn('GateInfo not initialized, returning default')
      return {
        id: 'all',
        name: 'Default Gate',
        type: 'monitoring',
        location: 'Unknown',
        color: '#2196F3',
        icon: '🏢',
        port: null
      }
    }
    
    return this.gateInfo[gate] || this.gateInfo['all']
  }

  // Get all available gates
  getAllGates() {
    return this.gateInfo
  }

  // Check if current gate is specific gate
  isGateSpecific() {
    return this.currentGate !== 'all'
  }

  // Check if current gate is gate_in
  isGateIn() {
    return this.currentGate === 'gate_in'
  }

  // Check if current gate is gate_out
  isGateOut() {
    return this.currentGate === 'gate_out'
  }

  // Check if monitoring all gates
  isMonitoringAll() {
    return this.currentGate === 'all'
  }

  // Get filtered events for current gate
  shouldProcessEvent(eventData) {
    if (this.isMonitoringAll()) {
      return true // Terima semua events
    }

    // Filter berdasarkan gate
    if (eventData.gate && eventData.gate === this.currentGate) {
      return true
    }

    if (eventData.gate_id && eventData.gate_id === this.currentGate) {
      return true
    }

    // Events yang tidak spesifik gate (system events)
    if (!eventData.gate && !eventData.gate_id) {
      return false // Skip non-gate events untuk gate-specific view
    }

    return false
  }

  // Get gate-specific dashboard title
  getDashboardTitle() {
    const info = this.getGateInfo()
    return `${info.icon} ${info.name} - Dashboard`
  }

  // Get gate-specific theme color
  getThemeColor() {
    return this.getGateInfo().color
  }

  // Generate gate-specific URLs for auto-run setup
  getGateURLs(baseURL = window.location.origin) {
    return {
      gate_in: `${baseURL}?gate=gate_in`,
      gate_out: `${baseURL}?gate=gate_out`,
      monitoring: `${baseURL}?gate=all`
    }
  }

  // Auto-setup untuk kiosk mode (fullscreen, disable right-click, etc)
  setupKioskMode() {
    if (this.isGateSpecific()) {
      console.log('🖥️ Setting up Kiosk Mode for', this.getGateInfo().name)
      
      // Disable right-click context menu
      document.addEventListener('contextmenu', (e) => e.preventDefault())
      
      // Disable F12, Ctrl+Shift+I, etc
      document.addEventListener('keydown', (e) => {
        if (e.key === 'F12' || 
            (e.ctrlKey && e.shiftKey && e.key === 'I') ||
            (e.ctrlKey && e.shiftKey && e.key === 'C') ||
            (e.ctrlKey && e.key === 'u')) {
          e.preventDefault()
        }
      })

      // Auto fullscreen (with user interaction)
      document.addEventListener('click', () => {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(console.warn)
        }
      }, { once: true })

      // Auto refresh setiap 6 jam untuk stability
      setTimeout(() => {
        window.location.reload()
      }, 6 * 60 * 60 * 1000)
    }
  }

  // Generate browser shortcut command untuk auto-run
  generateAutoRunCommand(baseURL = 'http://localhost:5173') {
    const urls = this.getGateURLs(baseURL)
    
    return {
      gate_in: `start chrome --kiosk --disable-web-security --disable-features=VizDisplayCompositor "${urls.gate_in}"`,
      gate_out: `start chrome --kiosk --disable-web-security --disable-features=VizDisplayCompositor "${urls.gate_out}"`,
      monitoring: `start chrome --new-window "${urls.monitoring}"`
    }
  }

  // Export konfigurasi untuk auto-run setup
  exportAutoRunBatch() {
    const commands = this.generateAutoRunCommand()
    
    const gateInBatch = `@echo off
echo Starting Gate IN Dashboard...
${commands.gate_in}
`

    const gateOutBatch = `@echo off
echo Starting Gate OUT Dashboard...
${commands.gate_out}
`

    const monitoringBatch = `@echo off
echo Starting Monitoring Dashboard...
${commands.monitoring}
`

    return {
      'start_gate_in.bat': gateInBatch,
      'start_gate_out.bat': gateOutBatch,
      'start_monitoring.bat': monitoringBatch
    }
  }

  // Setup event listeners untuk gate changes
  onGateChange(callback) {
    window.addEventListener('gateChanged', (event) => {
      callback(event.detail)
    })
  }

  // Clean up event listeners
  offGateChange(callback) {
    window.removeEventListener('gateChanged', callback)
  }
}

// Export singleton instance
export const gateConfig = new GateConfigService()
export default gateConfig

// Auto-setup kiosk mode saat import
if (typeof window !== 'undefined') {
  // Setup kiosk mode untuk gate-specific views
  document.addEventListener('DOMContentLoaded', () => {
    gateConfig.setupKioskMode()
  })
}

// Named exports
export const getCurrentGate = () => gateConfig.getCurrentGate()
export const getGateInfo = (gateId) => gateConfig.getGateInfo(gateId)
export const setCurrentGate = (gateId) => gateConfig.setCurrentGate(gateId)
export const clearStoredGate = () => gateConfig.clearStoredGate()
export const isGateSpecific = () => gateConfig.isGateSpecific()
export const isGateIn = () => gateConfig.isGateIn()
export const isGateOut = () => gateConfig.isGateOut()
export const shouldProcessEvent = (eventData) => gateConfig.shouldProcessEvent(eventData)
export const getDashboardTitle = () => gateConfig.getDashboardTitle()
export const getThemeColor = () => gateConfig.getThemeColor() 