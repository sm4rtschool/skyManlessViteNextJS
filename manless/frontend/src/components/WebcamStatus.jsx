import React, { useState, useEffect, useRef } from 'react'
import { Card } from './ui/card'
import { Camera, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react'

const WebcamStatus = () => {
  const [status, setStatus] = useState('checking')
  const [error, setError] = useState(null)
  const [devices, setDevices] = useState([])
  const [permission, setPermission] = useState('unknown')
  const [isTesting, setIsTesting] = useState(false)
  const videoRef = useRef(null)

  const checkWebcamStatus = async () => {
    setIsTesting(true)
    setStatus('checking')
    setError(null)

    try {
      console.log('🔍 Checking webcam status...')

      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('getUserMedia tidak didukung di browser ini')
      }

      // Check available devices first
      try {
        const allDevices = await navigator.mediaDevices.enumerateDevices()
        const videoDevices = allDevices.filter(device => device.kind === 'videoinput')
        setDevices(videoDevices)
        console.log('📹 Available video devices:', videoDevices)

        if (videoDevices.length === 0) {
          throw new Error('Tidak ada webcam yang terdeteksi')
        }
      } catch (deviceError) {
        console.warn('⚠️ Cannot enumerate devices:', deviceError)
        setDevices([])
      }

      // Try to get user media
      console.log('🎥 Requesting camera permission...')
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 }
        } 
      })

      console.log('✅ Camera access granted!')
      setStatus('connected')
      setPermission('granted')

      // Set video stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }

      // Log stream info
      const videoTrack = stream.getVideoTracks()[0]
      if (videoTrack) {
        console.log('📹 Video track info:', {
          label: videoTrack.label,
          enabled: videoTrack.enabled,
          readyState: videoTrack.readyState,
          settings: videoTrack.getSettings()
        })
      }

    } catch (err) {
      console.error('❌ Webcam check failed:', err)
      setStatus('error')
      setError(err.message)
      
      if (err.name === 'NotAllowedError') {
        setPermission('denied')
      } else if (err.name === 'NotFoundError') {
        setPermission('notfound')
      } else {
        setPermission('error')
      }
    } finally {
      setIsTesting(false)
    }
  }

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject
      const tracks = stream.getTracks()
      tracks.forEach(track => {
        console.log('🛑 Stopping track:', track.label)
        track.stop()
      })
      videoRef.current.srcObject = null
    }
    setStatus('disconnected')
  }

  useEffect(() => {
    checkWebcamStatus()

    return () => {
      stopWebcam()
    }
  }, [])

  const getStatusIcon = () => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'checking':
        return <RefreshCw className="w-5 h-5 text-blue-600 animate-spin" />
      default:
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Webcam Connected'
      case 'error':
        return 'Webcam Error'
      case 'checking':
        return 'Checking Webcam...'
      default:
        return 'Webcam Disconnected'
    }
  }

  const getPermissionText = () => {
    switch (permission) {
      case 'granted':
        return '✅ Permission Granted'
      case 'denied':
        return '❌ Permission Denied'
      case 'notfound':
        return '⚠️ No Camera Found'
      case 'error':
        return '❌ Access Error'
      default:
        return '❓ Unknown'
    }
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Camera className="w-6 h-6 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-800">Webcam Status Check</h3>
        </div>
        <button
          onClick={checkWebcamStatus}
          disabled={isTesting}
          className="flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${isTesting ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="space-y-4">
        {/* Status Display */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-2">
            {getStatusIcon()}
            <span className="font-medium text-gray-700">{getStatusText()}</span>
          </div>
          <div className="text-sm text-gray-600">
            <div>Permission: {getPermissionText()}</div>
            <div>Devices Found: {devices.length}</div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-medium text-red-800 mb-2">Error Details</h4>
            <p className="text-sm text-red-700">{error}</p>
            <div className="mt-2 text-xs text-red-600">
              <p>• Pastikan browser mengizinkan akses kamera</p>
              <p>• Cek apakah webcam tidak sedang digunakan aplikasi lain</p>
              <p>• Coba refresh halaman dan izinkan permission</p>
            </div>
          </div>
        )}

        {/* Device List */}
        {devices.length > 0 && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 mb-2">Available Cameras</h4>
            <div className="space-y-1">
              {devices.map((device, index) => (
                <div key={index} className="text-sm text-gray-600">
                  • {device.label || `Camera ${index + 1}`}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Video Preview */}
        {status === 'connected' && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 mb-2">Live Preview</h4>
            <div className="relative bg-black rounded overflow-hidden" style={{ height: '200px' }}>
              <video 
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
                onLoadedMetadata={() => console.log('✅ Video metadata loaded')}
                onCanPlay={() => console.log('✅ Video can play')}
                onError={(e) => console.error('❌ Video error:', e)}
              />
            </div>
            <button
              onClick={stopWebcam}
              className="mt-2 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              Stop Webcam
            </button>
          </div>
        )}

        {/* Troubleshooting Tips */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-800 mb-2">Troubleshooting Tips</h4>
          <div className="text-sm text-blue-700 space-y-1">
            <p>1. Klik icon kamera di address bar browser dan pilih "Allow"</p>
            <p>2. Pastikan tidak ada aplikasi lain yang menggunakan webcam</p>
            <p>3. Coba refresh halaman dan izinkan permission lagi</p>
            <p>4. Jika menggunakan Chrome, cek chrome://settings/content/camera</p>
            <p>5. Pastikan webcam tidak dinonaktifkan di Device Manager</p>
          </div>
        </div>
      </div>
    </Card>
  )
}

export default WebcamStatus 