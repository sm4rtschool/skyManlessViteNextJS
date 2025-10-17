import React, { useState, useEffect } from 'react'
import { gateConfig } from '../services/gateConfig.js'
import { wsService } from '../services/websocket.js'
import { apiService } from '../services/api.js'
import GateSelector from './GateSelector.jsx'
import SystemStats from './SystemStats.jsx'
import LiveView from './LiveView.jsx'
import LogViewer from './LogViewer.jsx'

const MonitoringCenter = () => {
  const [systemStatus, setSystemStatus] = useState({
    coordinator: { status: 'offline', active_sessions: 0 },
    gates: {
      gate_in: { status: 'offline', camera: false, arduino: false, card_reader: false },
      gate_out: { status: 'offline', camera: false, arduino: false, card_reader: false }
    }
  })
  
  const [parkingStats, setParkingStats] = useState({
    totalVehicles: 0,
    todayEntries: 0,
    currentOccupancy: 0,
    capacity: 100
  })

  const [recentEvents, setRecentEvents] = useState([])
  const [connectionStatus, setConnectionStatus] = useState('DISCONNECTED')

  useEffect(() => {
    // WebSocket event listeners
    const handleConnected = () => {
      setConnectionStatus('CONNECTED')
      addEvent('🟢 Monitoring Center terhubung ke sistem', 'success')
    }

    const handleDisconnected = () => {
      setConnectionStatus('DISCONNECTED')
      addEvent('🔴 Monitoring Center terputus dari sistem', 'error')
    }

    const handleSystemStatus = (data) => {
      setSystemStatus(data)
      
      // Update parking stats
      if (data.coordinator) {
        setParkingStats(prev => ({
          ...prev,
          totalVehicles: data.coordinator.active_sessions || 0,
          currentOccupancy: data.coordinator.active_sessions || 0
        }))
      }
    }

    const handleParkingEvent = (data) => {
      const eventType = data.event === 'entry' ? 'masuk' : 'keluar'
      const gateName = data.gate === 'gate_in' ? 'Gate Masuk' : 'Gate Keluar'
      addEvent(`🚗 Kendaraan ${eventType} di ${gateName} - ${data.result.card_id}`, 'info')
      
      // Update stats
      if (data.event === 'entry') {
        setParkingStats(prev => ({
          ...prev,
          todayEntries: prev.todayEntries + 1,
          currentOccupancy: prev.currentOccupancy + 1
        }))
      } else {
        setParkingStats(prev => ({
          ...prev,
          currentOccupancy: Math.max(0, prev.currentOccupancy - 1)
        }))
      }
    }

    const handleGateEvent = (data) => {
      const gateName = data.gate === 'gate_in' ? 'Gate Masuk' : 'Gate Keluar'
      const action = data.action === 'open' ? 'dibuka' : 'ditutup'
      addEvent(`🚪 ${gateName} ${action}`, 'info')
    }

    const handleCameraEvent = (data) => {
      const gateName = data.gate === 'gate_in' ? 'Gate Masuk' : 'Gate Keluar'
      addEvent(`📸 Foto diambil di ${gateName}`, 'success')
    }

    const handleCardEvent = (data) => {
      const gateName = data.gate === 'gate_in' ? 'Gate Masuk' : 'Gate Keluar'
      const status = data.status === 'valid' ? 'valid' : 'tidak valid'
      addEvent(`💳 Kartu ${status} di ${gateName} - ${data.card_id}`, 
               data.status === 'valid' ? 'success' : 'warning')
    }

    // Subscribe to WebSocket events
    wsService.on('connected', handleConnected)
    wsService.on('disconnected', handleDisconnected)
    wsService.on('system_status', handleSystemStatus)
    wsService.on('parking_event', handleParkingEvent)
    wsService.on('gate_event', handleGateEvent)
    wsService.on('camera_event', handleCameraEvent)
    wsService.on('card_event', handleCardEvent)

    // Request initial data
    wsService.requestSystemStatus()
    loadInitialData()

    // Periodic updates
    const interval = setInterval(() => {
      wsService.requestSystemStatus()
    }, 10000) // Every 10 seconds

    return () => {
      wsService.off('connected', handleConnected)
      wsService.off('disconnected', handleDisconnected)
      wsService.off('system_status', handleSystemStatus)
      wsService.off('parking_event', handleParkingEvent)
      wsService.off('gate_event', handleGateEvent)
      wsService.off('camera_event', handleCameraEvent)
      wsService.off('card_event', handleCardEvent)
      clearInterval(interval)
    }
  }, [])

  const loadInitialData = async () => {
    try {
      const systemData = await apiService.getSystemStatus()
      setSystemStatus(systemData)
      
      const capacity = await apiService.getParkingCapacity()
      setParkingStats(prev => ({
        ...prev,
        capacity: capacity.total || 100,
        currentOccupancy: capacity.occupied || 0,
        availableSlots: capacity.available || 100
      }))
    } catch (error) {
      console.error('Error loading initial data:', error)
    }
  }

  const addEvent = (message, type = 'info') => {
    const newEvent = {
      id: Date.now(),
      time: new Date(),
      message,
      type
    }
    setRecentEvents(prev => [newEvent, ...prev.slice(0, 9)]) // Keep last 10 events
  }

  const getGateStatusColor = (gateData) => {
    if (!gateData || gateData.status === 'offline') return '#F44336'
    const allConnected = gateData.camera && gateData.arduino && gateData.card_reader
    return allConnected ? '#4CAF50' : '#FF9800'
  }

  const getGateStatusText = (gateData) => {
    if (!gateData || gateData.status === 'offline') return 'OFFLINE'
    const connectedCount = [gateData.camera, gateData.arduino, gateData.card_reader].filter(Boolean).length
    return `${connectedCount}/3 ONLINE`
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
              🏢 Monitoring Center
            </h1>
            <p className="text-gray-600">
              Control Center - Monitoring Terpusat Semua Gate
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                connectionStatus === 'CONNECTED' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}></div>
              <span className={`text-sm font-medium ${
                connectionStatus === 'CONNECTED' ? 'text-green-600' : 'text-red-600'
              }`}>
                {connectionStatus}
              </span>
            </div>
            
            {/* Current Time */}
            <div className="text-sm text-gray-500">
              {new Date().toLocaleString('id-ID')}
            </div>
          </div>
        </div>
      </div>

      {/* Gate Selector */}
      <div className="mb-6">
        <GateSelector showSelector={true} />
      </div>

      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Coordinator Status */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">🖥️ Central Hub</h3>
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${
              systemStatus.coordinator?.status === 'online' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {systemStatus.coordinator?.status?.toUpperCase() || 'UNKNOWN'}
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Active Sessions:</span>
              <span className="font-medium">{systemStatus.coordinator?.active_sessions || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Last Update:</span>
              <span className="font-medium text-xs">
                {systemStatus.coordinator?.timestamp 
                  ? new Date(systemStatus.coordinator.timestamp).toLocaleTimeString('id-ID')
                  : 'N/A'
                }
              </span>
            </div>
          </div>
        </div>

        {/* Gate IN Status */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">🚪➡️ Gate Masuk</h3>
            <div 
              className="px-3 py-1 rounded-full text-xs font-medium text-white"
              style={{ backgroundColor: getGateStatusColor(systemStatus.gates?.gate_in) }}
            >
              {getGateStatusText(systemStatus.gates?.gate_in)}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="text-center">
              <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${
                systemStatus.gates?.gate_in?.camera ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-gray-600">Camera</span>
            </div>
            <div className="text-center">
              <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${
                systemStatus.gates?.gate_in?.arduino ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-gray-600">Arduino</span>
            </div>
            <div className="text-center">
              <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${
                systemStatus.gates?.gate_in?.card_reader ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-gray-600">Card</span>
            </div>
          </div>
        </div>

        {/* Gate OUT Status */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">🚪⬅️ Gate Keluar</h3>
            <div 
              className="px-3 py-1 rounded-full text-xs font-medium text-white"
              style={{ backgroundColor: getGateStatusColor(systemStatus.gates?.gate_out) }}
            >
              {getGateStatusText(systemStatus.gates?.gate_out)}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="text-center">
              <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${
                systemStatus.gates?.gate_out?.camera ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-gray-600">Camera</span>
            </div>
            <div className="text-center">
              <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${
                systemStatus.gates?.gate_out?.arduino ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-gray-600">Arduino</span>
            </div>
            <div className="text-center">
              <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${
                systemStatus.gates?.gate_out?.card_reader ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-gray-600">Card</span>
            </div>
          </div>
        </div>
      </div>

      {/* System Statistics */}
      <SystemStats stats={parkingStats} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Live View - Spans 2 columns */}
        <div className="xl:col-span-2">
          <LiveView />
        </div>

        {/* Recent Events */}
        <div className="xl:col-span-1">
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              📊 Recent Events
            </h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {recentEvents.length > 0 ? (
                recentEvents.map(event => (
                  <div key={event.id} className="border-l-4 pl-3 py-2" style={{
                    borderLeftColor: 
                      event.type === 'success' ? '#4CAF50' :
                      event.type === 'warning' ? '#FF9800' :
                      event.type === 'error' ? '#F44336' : '#2196F3'
                  }}>
                    <div className="text-sm font-medium text-gray-800">
                      {event.message}
                    </div>
                    <div className="text-xs text-gray-500">
                      {event.time.toLocaleTimeString('id-ID')}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <div className="text-4xl mb-2">📭</div>
                  <div>Menunggu aktivitas...</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Log Viewer - Full Width */}
      <div className="w-full">
        <LogViewer />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">🎮 Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => wsService.requestSystemStatus()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            🔄 Refresh Status
          </button>
          <button 
            onClick={() => wsService.captureImageGateIn()}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            📸 Capture Gate IN
          </button>
          <button 
            onClick={() => wsService.captureImageGateOut()}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            📸 Capture Gate OUT
          </button>
          <button 
            onClick={() => window.open('?gate=gate_in', '_blank')}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            🖥️ Open Gate IN
          </button>
        </div>
      </div>
    </div>
  )
}

export default MonitoringCenter 