import React, { useState, useEffect } from 'react'
import { gateConfig } from '../services/gateConfig.js'
import LiveView from '../components/LiveView'
import LogViewer from '../components/LogViewer'
import CardReader from '../components/CardReader'
import GateControl from '../components/GateControl'
import SystemStats from '../components/SystemStats'
import GateSelector from '../components/GateSelector'
import GateSpecificDashboard from '../components/GateSpecificDashboard'
import SimpleDashboard from '../components/SimpleDashboard'
import GateOperationalInterface from '../components/GateOperationalInterface'
import MonitoringCenter from '../components/MonitoringCenter'
import LoadingScreen from '../components/LoadingScreen'
import CameraTest from '../components/CameraTest'
import SystemDebug from '../components/SystemDebug'
import WebcamStatus from '../components/WebcamStatus'
import { apiService } from '../services/api'
import { wsService } from '../services/websocket'

const Dashboard = () => {
  const [currentGate, setCurrentGate] = useState(gateConfig.getCurrentGate())
  const [gateInfo, setGateInfo] = useState(gateConfig.getGateInfo())
  const [isLoading, setIsLoading] = useState(true)
  const [systemStatus, setSystemStatus] = useState({
    camera: false,
    cardReader: false,
    arduino: false,
    gate: 'unknown'
  })

  const [parkingStats, setParkingStats] = useState({
    totalVehicles: 0,
    todayEntries: 0,
    currentOccupancy: 0,
    capacity: 100
  })

  useEffect(() => {
    // Listen untuk gate changes
    const handleGateChange = (event) => {
      setCurrentGate(event.detail.gateId)
      setGateInfo(event.detail.gateInfo)
    }

    gateConfig.onGateChange(handleGateChange)

    return () => {
      gateConfig.offGateChange(handleGateChange)
    }
  }, [])

  useEffect(() => {
    // Inisialisasi koneksi ke backend
    const initializeSystem = async () => {
      try {
        // Test koneksi API dengan timeout dan retry
        let systemStatus = null
        let retryCount = 0
        const maxRetries = 3
        
        while (retryCount < maxRetries && !systemStatus) {
          try {
            console.log(`🔍 Attempting API call (${retryCount + 1}/${maxRetries})...`)
            systemStatus = await apiService.getSystemStatus()
            console.log('✅ Backend system status:', systemStatus)
            break
          } catch (apiError) {
            console.warn(`⚠️ API attempt ${retryCount + 1} failed:`, apiError.message)
            retryCount++
            if (retryCount < maxRetries) {
              console.log(`🔄 Retrying in ${retryCount * 1000}ms...`)
              await new Promise(resolve => setTimeout(resolve, retryCount * 1000))
            }
          }
        }

        // Set parking stats dari system status jika berhasil
        if (systemStatus && systemStatus.coordinator) {
          setParkingStats({
            totalVehicles: systemStatus.coordinator.active_sessions || 0,
            todayEntries: systemStatus.coordinator.active_sessions || 0,
            currentOccupancy: systemStatus.coordinator.active_sessions || 0,
            capacity: 100
          })
        }

        // Update system status dari response API jika berhasil
        if (systemStatus && systemStatus.hardware) {
          console.log('📊 Updating status from API:', systemStatus.hardware);
          const { camera, arduino, card_reader } = systemStatus.hardware;

          setSystemStatus(prev => ({
            ...prev,
            camera: camera?.connected ?? false,
            cardReader: card_reader?.connected ?? false,
            arduino: arduino?.connected ?? false,
            gate: arduino?.gate_status?.split(',')[0] ?? 'unknown'
          }));
        } else {
          console.warn('⚠️ API response missing "hardware" object, or API failed. Using fallback status.');
          // Fallback: set status unknown, akan diupdate via WebSocket
          setSystemStatus({
            camera: false,
            cardReader: false,
            arduino: false,
            gate: 'unknown'
          });
        }

        // Connect WebSocket hanya jika belum connected
        if (!wsService.isConnected()) {
          console.log('🔗 Connecting to WebSocket...')
          wsService.connect()
        } else {
          console.log('✅ WebSocket already connected')
        }
        
        // Setup WebSocket listeners dengan cleanup yang lebih baik
        const handleSystemMessage = (data) => {
          console.log('📨 System WebSocket message:', data)
          if (data.type === 'connected') {
            // Request system status setelah terhubung
            console.log('🔄 Requesting system status via WebSocket...')
            wsService.requestSystemStatus()
          }
        }

        const handleGateMessage = (data) => {
          console.log('🚪 Gate status:', data)
          setSystemStatus(prev => ({
            ...prev,
            gate: data.status || 'closed'
          }))
        }

        // BUAT LISTENER BARU UNTUK 'hardware_status' YANG REAL-TIME
        const handleHardwareStatusUpdate = (data) => {
          console.log('%c>>> 🔧 REALTIME HARDWARE STATUS UPDATE RECEIVED 🔧 <<<', 'color: #2e7d32; font-weight: bold; font-size: 14px;');
          console.log('Raw data from WebSocket:', data);

          if (data && data.payload) {
            const hardware = data.payload;
            console.log('Extracted hardware payload:', hardware);

            setSystemStatus(prev => {
              console.log('State BEFORE update:', prev);
              const newState = {
                ...prev,
                camera: hardware.camera?.connected ?? prev.camera,
                arduino: hardware.arduino?.connected ?? prev.arduino,
                cardReader: hardware.card_reader?.connected ?? prev.cardReader,
                gate: hardware.arduino?.gate_status?.split(',')[0] ?? prev.gate,
              };
              console.log('%cState AFTER update:', 'color: #1976d2; font-weight: bold;', newState);
              return newState;
            });
          } else {
            console.warn('No payload in hardware status update.');
          }
          console.log('--- End of Hardware Status Update ---');
        };

        wsService.on('system', handleSystemMessage)
        wsService.on('gate', handleGateMessage)
        
        // DAFTARKAN LISTENER BARU YANG BENAR
        wsService.on('hardware_status', handleHardwareStatusUpdate)

        console.log('✅ Sistem berhasil terhubung ke backend!')
      } catch (error) {
        console.error('❌ Gagal menghubungkan ke backend:', error)
        // Set status error tapi tetap coba WebSocket
        setSystemStatus({
          camera: false,
          cardReader: false,
          arduino: false,
          gate: 'error'
        })
        
        // Tetap coba WebSocket untuk fallback
        if (!wsService.isConnected()) {
          console.log('🔗 Trying WebSocket as fallback...')
          wsService.connect()
        }
      } finally {
        // Hide loading setelah initialization
        setTimeout(() => setIsLoading(false), 1500)
      }
    }

    initializeSystem()

    // Cleanup saat component unmount
    return () => {
      // Clean up listeners
      wsService.off('system')
      wsService.off('gate')
      wsService.off('system_status')
      wsService.off('hardware_status')
    }
  }, [])

  // Show loading screen
  if (isLoading) {
    return <LoadingScreen message="Menghubungkan ke sistem..." />
  }

  // Debug logging untuk gate detection
  console.log('🔍 Dashboard routing debug:', {
    currentGate: gateConfig.getCurrentGate(),
    isGateSpecific: gateConfig.isGateSpecific(),
    isMonitoringAll: gateConfig.isMonitoringAll(),
    gateInfo: gateConfig.getGateInfo()
  })

  // Jika gate-specific (untuk monitor kiosk), tampilkan interface operasional
  if (gateConfig.isGateSpecific()) {
    console.log('🚪 Rendering GateOperationalInterface for:', gateConfig.getCurrentGate())
    // Interface operasional utama untuk setiap gate
    return <GateOperationalInterface />
    
    // Fallback options untuk debugging:
    // return <SimpleDashboard />
    // return <GateSpecificDashboard />
  }

  // Jika monitoring center (tanpa parameter gate atau gate=all), tampilkan monitoring center
  if (gateConfig.isMonitoringAll()) {
    console.log('🏢 Rendering MonitoringCenter for all gates')
    return <MonitoringCenter />
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header dengan gate info */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {gateConfig.getDashboardTitle()}
            </h1>
            <p className="text-gray-600">
              {gateConfig.isMonitoringAll() 
                ? 'Control Center - Monitoring Terpusat' 
                : `Monitor ${gateInfo.name} - ${gateInfo.location}`
              }
            </p>
          </div>
          
          {/* Gate Info Badge */}
          <GateSelector showSelector={false} />
        </div>
      </div>

      {/* Gate Selector untuk switching */}
      <div className="mb-8">
        <GateSelector showSelector={true} />
      </div>

      {/* System Statistics */}
      <SystemStats stats={parkingStats} />

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Live Camera View */}
        <div className="xl:col-span-1">
          <LiveView />
        </div>

        {/* Card Reader & Gate Control */}
        <div className="xl:col-span-1 space-y-6">
          <CardReader />
          <GateControl 
            gateStatus={systemStatus.gate}
            onGateControl={(action) => {
              console.log('Gate action:', action)
              console.log(`Gate ${action === 'open' ? 'dibuka' : 'ditutup'}`)
              
              // Kirim command ke backend via WebSocket
              wsService.controlGate(action)
              
              // Update status lokal (akan di-override oleh response WebSocket)
              setSystemStatus(prev => ({
                ...prev,
                gate: action
              }))
            }}
          />
        </div>
      </div>

      {/* Camera Test - Full Width */}
      <div className="w-full">
        <CameraTest />
      </div>

      {/* Webcam Status - Full Width */}
      <div className="w-full">
        <WebcamStatus />
      </div>

      {/* System Debug - Full Width */}
      <div className="w-full">
        <SystemDebug />
      </div>

      {/* Log Viewer - Full Width */}
      <div className="w-full">
        <LogViewer />
      </div>

      {/* System Status Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus.camera ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium text-gray-700">Kamera</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus.cardReader ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium text-gray-700">Card Reader</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus.arduino ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium text-gray-700">Arduino</span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              systemStatus.gate === 'open' ? 'bg-yellow-500' : 'bg-green-500'
            }`}></div>
            <span className="text-sm font-medium text-gray-700">
              Gate: {systemStatus.gate === 'open' ? 'Terbuka' : 'Tertutup'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 