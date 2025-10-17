import React, { useState, useEffect } from 'react'
import { Card } from './ui/card'
import { Bug, RefreshCw, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { gateConfig, clearStoredGate } from '../services/gateConfig'

const SystemDebug = () => {
  const [debugInfo, setDebugInfo] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [showDebug, setShowDebug] = useState(false)

  const checkSystemStatus = async () => {
    setIsLoading(true)
    const info = {}

    try {
      // Check browser capabilities
      info.browser = {
        userAgent: navigator.userAgent,
        isChrome: navigator.userAgent.includes('Chrome'),
        isFirefox: navigator.userAgent.includes('Firefox'),
        isSafari: navigator.userAgent.includes('Safari'),
        isEdge: navigator.userAgent.includes('Edge')
      }

      // Check media devices support
      info.mediaDevices = {
        supported: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
        enumerateDevices: !!(navigator.mediaDevices && navigator.mediaDevices.enumerateDevices)
      }

      // Check available devices
      if (info.mediaDevices.enumerateDevices) {
        try {
          const devices = await navigator.mediaDevices.enumerateDevices()
          info.availableDevices = {
            videoInputs: devices.filter(d => d.kind === 'videoinput'),
            audioInputs: devices.filter(d => d.kind === 'audioinput'),
            audioOutputs: devices.filter(d => d.kind === 'audiooutput')
          }
        } catch (error) {
          info.availableDevices = { error: error.message }
        }
      }

      // Check permissions
      info.permissions = {
        protocol: window.location.protocol,
        isSecure: window.location.protocol === 'https:',
        hostname: window.location.hostname,
        port: window.location.port
      }

      // Check WebSocket connection
      info.websocket = {
        supported: typeof WebSocket !== 'undefined',
        url: 'ws://localhost:8765' // Default WebSocket URL
      }

      // Check localStorage
      info.storage = {
        localStorage: typeof localStorage !== 'undefined',
        sessionStorage: typeof sessionStorage !== 'undefined'
      }

      // Check screen info
      info.screen = {
        width: window.screen.width,
        height: window.screen.height,
        availWidth: window.screen.availWidth,
        availHeight: window.screen.availHeight,
        colorDepth: window.screen.colorDepth,
        pixelDepth: window.screen.pixelDepth
      }

      // Check window info
      info.window = {
        innerWidth: window.innerWidth,
        innerHeight: window.innerHeight,
        outerWidth: window.outerWidth,
        outerHeight: window.outerHeight
      }

      // Test webcam access
      if (info.mediaDevices.supported) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ video: true })
          info.webcamTest = {
            success: true,
            tracks: stream.getTracks().map(track => ({
              kind: track.kind,
              label: track.label,
              enabled: track.enabled,
              readyState: track.readyState
            }))
          }
          // Stop the stream immediately
          stream.getTracks().forEach(track => track.stop())
        } catch (error) {
          info.webcamTest = {
            success: false,
            error: error.message,
            name: error.name
          }
        }
      }

      setDebugInfo(info)
    } catch (error) {
      console.error('Debug check failed:', error)
      info.error = error.message
      setDebugInfo(info)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    checkSystemStatus()
  }, [])

  useEffect(() => {
    const updateDebugInfo = () => {
      setDebugInfo({
        currentGate: gateConfig.getCurrentGate(),
        gateInfo: gateConfig.getGateInfo(),
        isGateSpecific: gateConfig.isGateSpecific(),
        isMonitoringAll: gateConfig.isMonitoringAll(),
        urlParams: new URLSearchParams(window.location.search).toString(),
        localStorage: localStorage.getItem('selected_gate'),
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
      })
    }

    updateDebugInfo()
    const interval = setInterval(updateDebugInfo, 2000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (condition) => {
    if (condition === true) return <CheckCircle className="w-4 h-4 text-green-600" />
    if (condition === false) return <XCircle className="w-4 h-4 text-red-600" />
    return <AlertTriangle className="w-4 h-4 text-yellow-600" />
  }

  const getStatusColor = (condition) => {
    if (condition === true) return 'text-green-600'
    if (condition === false) return 'text-red-600'
    return 'text-yellow-600'
  }

  const handleClearLocalStorage = () => {
    clearStoredGate()
    window.location.reload()
  }

  const handleTestGate = (gateId) => {
    const url = new URL(window.location)
    url.searchParams.set('gate', gateId)
    window.location.href = url.toString()
  }

  if (!showDebug) {
    return (
      <div className="bg-gray-100 rounded-lg p-4">
        <button
          onClick={() => setShowDebug(true)}
          className="text-sm text-gray-600 hover:text-gray-800"
        >
          🔧 Show Debug Info
        </button>
      </div>
    )
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Bug className="w-6 h-6 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-800">System Debug Info</h3>
        </div>
        <button
          onClick={checkSystemStatus}
          disabled={isLoading}
          className="flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {isLoading && (
        <div className="text-center py-4">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
          <p className="text-gray-600">Checking system status...</p>
        </div>
      )}

      {!isLoading && Object.keys(debugInfo).length > 0 && (
        <div className="space-y-4">
          {/* Browser Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 mb-2">Browser Information</h4>
            <div className="text-sm space-y-1">
              <div className="flex items-center space-x-2">
                {getStatusIcon(debugInfo.browser?.isChrome || debugInfo.browser?.isFirefox)}
                <span className={getStatusColor(debugInfo.browser?.isChrome || debugInfo.browser?.isFirefox)}>
                  {debugInfo.browser?.isChrome ? 'Chrome' : debugInfo.browser?.isFirefox ? 'Firefox' : 'Other Browser'}
                </span>
              </div>
              <p className="text-xs text-gray-500 truncate">{debugInfo.browser?.userAgent}</p>
            </div>
          </div>

          {/* Media Devices */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 mb-2">Media Devices</h4>
            <div className="text-sm space-y-1">
              <div className="flex items-center space-x-2">
                {getStatusIcon(debugInfo.mediaDevices?.supported)}
                <span className={getStatusColor(debugInfo.mediaDevices?.supported)}>
                  getUserMedia: {debugInfo.mediaDevices?.supported ? 'Supported' : 'Not Supported'}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(debugInfo.mediaDevices?.enumerateDevices)}
                <span className={getStatusColor(debugInfo.mediaDevices?.enumerateDevices)}>
                  enumerateDevices: {debugInfo.mediaDevices?.enumerateDevices ? 'Supported' : 'Not Supported'}
                </span>
              </div>
            </div>
          </div>

          {/* Available Devices */}
          {debugInfo.availableDevices && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-700 mb-2">Available Devices</h4>
              <div className="text-sm space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="text-gray-600">Video Inputs:</span>
                  <span className="font-medium">{debugInfo.availableDevices.videoInputs?.length || 0}</span>
                </div>
                {debugInfo.availableDevices.videoInputs?.map((device, index) => (
                  <div key={index} className="text-xs text-gray-500 ml-4">
                    • {device.label || `Camera ${index + 1}`}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Permissions */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 mb-2">Permissions & Security</h4>
            <div className="text-sm space-y-1">
              <div className="flex items-center space-x-2">
                {getStatusIcon(debugInfo.permissions?.isSecure)}
                <span className={getStatusColor(debugInfo.permissions?.isSecure)}>
                  HTTPS: {debugInfo.permissions?.isSecure ? 'Secure' : 'HTTP (may need HTTPS)'}
                </span>
              </div>
              <div className="text-xs text-gray-500">
                Protocol: {debugInfo.permissions?.protocol} | 
                Host: {debugInfo.permissions?.hostname} | 
                Port: {debugInfo.permissions?.port}
              </div>
            </div>
          </div>

          {/* Webcam Test */}
          {debugInfo.webcamTest && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-700 mb-2">Webcam Test</h4>
              <div className="text-sm space-y-1">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(debugInfo.webcamTest.success)}
                  <span className={getStatusColor(debugInfo.webcamTest.success)}>
                    Access: {debugInfo.webcamTest.success ? 'Success' : 'Failed'}
                  </span>
                </div>
                {!debugInfo.webcamTest.success && (
                  <div className="text-xs text-red-600 ml-4">
                    Error: {debugInfo.webcamTest.error} ({debugInfo.webcamTest.name})
                  </div>
                )}
                {debugInfo.webcamTest.success && debugInfo.webcamTest.tracks && (
                  <div className="text-xs text-gray-600 ml-4">
                    Tracks: {debugInfo.webcamTest.tracks.length}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Screen Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 mb-2">Display Information</h4>
            <div className="text-sm space-y-1">
              <div>Screen: {debugInfo.screen?.width} x {debugInfo.screen?.height}</div>
              <div>Window: {debugInfo.window?.innerWidth} x {debugInfo.window?.innerHeight}</div>
              <div>Color Depth: {debugInfo.screen?.colorDepth} bit</div>
            </div>
          </div>

          {/* Gate Detection Debug */}
          <div className="bg-white rounded p-3 space-y-2">
            <h4 className="font-medium">🚪 Gate Detection</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>Current Gate: <span className="font-mono bg-yellow-100 px-1 rounded">{debugInfo.currentGate}</span></div>
              <div>Gate Name: <span className="font-mono bg-yellow-100 px-1 rounded">{debugInfo.gateInfo?.name}</span></div>
              <div>Is Gate Specific: <span className="font-mono bg-yellow-100 px-1 rounded">{debugInfo.isGateSpecific?.toString()}</span></div>
              <div>Is Monitoring All: <span className="font-mono bg-yellow-100 px-1 rounded">{debugInfo.isMonitoringAll?.toString()}</span></div>
              <div>URL Params: <span className="font-mono bg-yellow-100 px-1 rounded">{debugInfo.urlParams}</span></div>
              <div>LocalStorage: <span className="font-mono bg-yellow-100 px-1 rounded">{debugInfo.localStorage || 'null'}</span></div>
            </div>
          </div>

          {/* Debug Actions */}
          <div className="bg-white rounded p-3 space-y-2">
            <h4 className="font-medium">🛠️ Debug Actions</h4>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={handleClearLocalStorage}
                className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
              >
                Clear LocalStorage
              </button>
              <button
                onClick={() => handleTestGate('gate_in')}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                Test Gate IN
              </button>
              <button
                onClick={() => handleTestGate('gate_out')}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                Test Gate OUT
              </button>
              <button
                onClick={() => handleTestGate('all')}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                Test Gate ALL
              </button>
              <button
                onClick={() => handleTestGate('gate_all')}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                Test Gate_ALL
              </button>
            </div>
          </div>

          {/* System Info */}
          <div className="bg-white rounded p-3 space-y-2">
            <h4 className="font-medium">💻 System Info</h4>
            <div className="text-sm space-y-1">
              <div>User Agent: <span className="font-mono bg-gray-100 px-1 rounded text-xs">{debugInfo.userAgent}</span></div>
              <div>Timestamp: <span className="font-mono bg-gray-100 px-1 rounded text-xs">{debugInfo.timestamp}</span></div>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}

export default SystemDebug 