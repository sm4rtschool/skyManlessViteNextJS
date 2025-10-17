import React, { useState, useEffect } from 'react'
import { Activity, Camera, Wifi, Users, TrendingUp, Clock, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { wsService } from '../services/websocket'
import { getSystemStatus } from '../services/api'

const SystemStats = () => {
  const [systemStatus, setSystemStatus] = useState({
    camera: false,
    arduino: false,
    card_reader: false,
    gate_status: 'closed'
  })
  const [cameraInfo, setCameraInfo] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [stats, setStats] = useState({
    vehicles_today: 0,
    vehicles_in_parking: 0,
    avg_parking_time: '0m',
    system_uptime: '0h 0m'
  })

  useEffect(() => {
    // Subscribe to WebSocket events
    wsService.on('system', handleSystemUpdate)
    wsService.on('camera', handleCameraUpdate)
    
    // Initial data load
    loadSystemData()
    
    // Connect WebSocket if not already connected
    if (!wsService.isConnected()) {
      wsService.connect()
    }

    return () => {
      wsService.off('system', handleSystemUpdate)
      wsService.off('camera', handleCameraUpdate)
    }
  }, [])

  const handleSystemUpdate = (data) => {
    if (data.type === 'connected') {
      setConnectionStatus('connected')
    } else if (data.type === 'disconnected') {
      setConnectionStatus('disconnected')
    } else if (data.type === 'system_status') {
      setSystemStatus(data)
    }
  }

  const handleCameraUpdate = (data) => {
    if (data.camera_info) {
      setCameraInfo(data.camera_info)
    }
  }

  const loadSystemData = async () => {
    try {
      // Load system status from API - FIXED: menggunakan endpoint yang benar
      const data = await getSystemStatus()
      console.log('System status from API:', data)
      
      // Extract hardware status from new backend response format
      if (data && data.gates && data.gates.gate_in) {
        const gateInData = data.gates.gate_in
        const controllerStatus = gateInData.controller_status
        
        if (controllerStatus && controllerStatus.hardware) {
          const hardware = controllerStatus.hardware
          
          setSystemStatus({
            camera: hardware.camera?.connected || false,
            arduino: hardware.arduino?.connected || false,
            card_reader: hardware.card_reader?.connected || false,
            gate_status: hardware.arduino?.gate?.status || 'closed'
          })
        }
        
        // Update connection status
        setConnectionStatus(gateInData.status === 'online' ? 'connected' : 'disconnected')
        
        // Update stats
        if (data.coordinator) {
          setStats(prev => ({
            ...prev,
            vehicles_in_parking: data.coordinator.active_sessions || 0
          }))
        }
      }
      
      // Load camera info
      const cameraResponse = await fetch('http://localhost:8000/api/camera/info')
      if (cameraResponse.ok) {
        const cameraData = await cameraResponse.json()
        setCameraInfo(cameraData)
      }
    } catch (error) {
      console.error('Error loading system data:', error)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case true:
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case false:
      case 'disconnected':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case true:
      case 'connected':
        return 'text-green-600 bg-green-100'
      case false:
      case 'disconnected':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-yellow-600 bg-yellow-100'
    }
  }

  const getCameraStatusText = () => {
    if (!cameraInfo) return 'Loading...'
    if (cameraInfo.connected) {
      return `${cameraInfo.source?.replace('_', ' ')} - ${cameraInfo.resolution}`
    }
    return 'Disconnected'
  }

  const isHikvisionCamera = () => {
    return cameraInfo?.source?.includes('192.168.200.64')
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center">
          <Activity className="w-5 h-5 mr-2 text-blue-600" />
          Status Sistem
        </h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          }`}></div>
          <span className={`text-sm ${
            connectionStatus === 'connected' ? 'text-green-600' : 'text-red-600'
          }`}>
            {connectionStatus === 'connected' ? 'Terhubung' : 'Terputus'}
          </span>
        </div>
      </div>

      {/* System Components Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {/* Camera Status */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Camera className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Kamera</span>
            </div>
            {getStatusIcon(systemStatus.camera)}
          </div>
          <div className="text-xs text-gray-600">
            {getCameraStatusText()}
          </div>
          {isHikvisionCamera() && (
            <div className="flex items-center mt-2 text-xs">
              <Wifi className="w-3 h-3 mr-1 text-blue-500" />
              <span className="text-blue-600 font-medium">Hikvision IP Cam</span>
            </div>
          )}
        </div>

        {/* Arduino Status */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Arduino</span>
            </div>
            {getStatusIcon(systemStatus.arduino)}
          </div>
          <div className="text-xs text-gray-600">
            Gate Controller
          </div>
        </div>

        {/* Card Reader Status */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Card Reader</span>
            </div>
            {getStatusIcon(systemStatus.card_reader)}
          </div>
          <div className="text-xs text-gray-600">
            RFID Reader
          </div>
        </div>
      </div>

      {/* Hikvision Camera Details */}
      {isHikvisionCamera() && cameraInfo && (
        <div className="bg-blue-50 rounded-lg p-4 mb-6">
          <h4 className="text-sm font-medium text-blue-900 mb-3 flex items-center">
            <Wifi className="w-4 h-4 mr-2" />
            Detail Kamera Hikvision
          </h4>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-blue-700 font-medium">IP Address:</span>
              <span className="ml-1">192.168.200.64</span>
            </div>
            <div>
              <span className="text-blue-700 font-medium">Protocol:</span>
              <span className="ml-1">RTSP</span>
            </div>
            <div>
              <span className="text-blue-700 font-medium">Resolution:</span>
              <span className="ml-1">{cameraInfo.resolution}</span>
            </div>
            <div>
              <span className="text-blue-700 font-medium">Stream Type:</span>
              <span className="ml-1">
                {cameraInfo.source?.includes('102') ? 'Sub Stream' : 'Main Stream'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Gate Status */}
      <div className="border-t border-gray-200 pt-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Status Pintu Gerbang</span>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            systemStatus.gate_status === 'open' 
              ? 'text-green-600 bg-green-100' 
              : 'text-gray-600 bg-gray-100'
          }`}>
            {systemStatus.gate_status === 'open' ? 'Terbuka' : 'Tertutup'}
          </span>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-4 border-t border-gray-200">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{stats.vehicles_today}</div>
          <div className="text-xs text-gray-500">Kendaraan Hari Ini</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{stats.vehicles_in_parking}</div>
          <div className="text-xs text-gray-500">Sedang Parkir</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-purple-600">{stats.avg_parking_time}</div>
          <div className="text-xs text-gray-500">Rata-rata Waktu Parkir</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-orange-600">{stats.system_uptime}</div>
          <div className="text-xs text-gray-500">System Uptime</div>
        </div>
      </div>
    </div>
  )
}

export default SystemStats 