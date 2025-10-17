import React, { useState, useEffect } from 'react'
import { Camera, Monitor, Wifi, Settings, Sliders, Save, RefreshCw, Star } from 'lucide-react'
import { apiService } from '../services/api'

const CameraSettings = ({ isOpen, onClose, onCameraChange }) => {
  const [availableCameras, setAvailableCameras] = useState([])
  const [cameraInfo, setCameraInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [customUrl, setCustomUrl] = useState('')
  const [cameraSettings, setCameraSettings] = useState({
    brightness: 50,
    contrast: 50,
    saturation: 50,
    exposure: 50
  })

  // Preset kamera Hikvision yang sudah dikonfigurasi
  const hikvisionPresets = [
    {
      id: 'hikvision-sub',
      name: 'Hikvision - Sub Stream (Recommended)',
      source: 'rtsp://admin:R4hasiabanget@192.168.200.64:554/Streaming/Channels/102/',
      type: 'ip_camera_rtsp',
      status: 'tested',
      resolution: '640x360',
      description: 'Kualitas rendah, streaming stabil',
      recommended: true
    },
    {
      id: 'hikvision-main',
      name: 'Hikvision - Main Stream (HD)',
      source: 'rtsp://admin:R4hasiabanget@192.168.200.64:554/Streaming/Channels/101/',
      type: 'ip_camera_rtsp',
      status: 'tested',
      resolution: '1920x1080',
      description: 'Kualitas tinggi, butuh bandwidth lebih'
    },
    {
      id: 'hikvision-h264',
      name: 'Hikvision - H.264 Stream',
      source: 'rtsp://admin:R4hasiabanget@192.168.200.64:554/h264/ch1/main/av_stream',
      type: 'ip_camera_rtsp',
      status: 'tested',
      resolution: '1920x1080',
      description: 'Format H.264 alternative'
    },
    {
      id: 'hikvision-cgi',
      name: 'Hikvision - CGI Stream',
      source: 'rtsp://admin:R4hasiabanget@192.168.200.64:554/cam/realmonitor?channel=1&subtype=0',
      type: 'ip_camera_rtsp',
      status: 'tested',
      resolution: '1920x1080',
      description: 'Format CGI alternative'
    }
  ]

  useEffect(() => {
    if (isOpen) {
      loadCameraData()
    }
  }, [isOpen])

  const loadCameraData = async () => {
    setLoading(true)
    try {
      const [cameras, info] = await Promise.all([
        apiService.getAvailableCameras(),
        apiService.getCameraInfo()
      ])
      
      setAvailableCameras(cameras.cameras || [])
      setCameraInfo(info)
    } catch (error) {
      console.error('Error loading camera data:', error)
    }
    setLoading(false)
  }

  const handleCameraSelect = async (source) => {
    setLoading(true)
    try {
      await apiService.setCameraSource(source)
      const updatedInfo = await apiService.getCameraInfo()
      setCameraInfo(updatedInfo)
      onCameraChange && onCameraChange(updatedInfo)
    } catch (error) {
      console.error('Error changing camera:', error)
    }
    setLoading(false)
  }

  const handleCustomCameraSubmit = async (e) => {
    e.preventDefault()
    if (customUrl.trim()) {
      await handleCameraSelect(customUrl.trim())
      setCustomUrl('')
    }
  }

  const handleSettingChange = async (property, value) => {
    try {
      await apiService.setCameraSettings(property, value / 100) // Convert to 0-1 range
      setCameraSettings(prev => ({ ...prev, [property]: value }))
    } catch (error) {
      console.error('Error updating camera setting:', error)
    }
  }

  const getCameraTypeIcon = (type) => {
    switch (type) {
      case 'webcam':
        return <Monitor className="w-5 h-5" />
      case 'ip_camera_http':
      case 'ip_camera_rtsp':
        return <Wifi className="w-5 h-5" />
      default:
        return <Camera className="w-5 h-5" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'available':
        return 'text-green-600 bg-green-100'
      case 'tested':
        return 'text-blue-600 bg-blue-100'
      case 'example':
        return 'text-orange-600 bg-orange-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'available':
        return 'Tersedia'
      case 'tested':
        return 'Teruji'
      case 'example':
        return 'Contoh'
      default:
        return 'Unknown'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        ></div>

        {/* Modal content */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-5xl sm:w-full">
          {/* Header */}
          <div className="bg-white px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Settings className="w-6 h-6 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Pengaturan Kamera
                </h3>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="bg-white px-6 py-4 max-h-96 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">Memuat...</span>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Current Camera Info */}
                {cameraInfo && (
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-blue-900 mb-2">Kamera Aktif</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-blue-700">Sumber:</span>
                        <span className="ml-1 font-medium break-all">{cameraInfo.camera_source}</span>
                      </div>
                      <div>
                        <span className="text-blue-700">Tipe:</span>
                        <span className="ml-1 font-medium">{cameraInfo.camera_type?.replace('_', ' ')}</span>
                      </div>
                      <div>
                        <span className="text-blue-700">Resolusi:</span>
                        <span className="ml-1 font-medium">{cameraInfo.width}x{cameraInfo.height}</span>
                      </div>
                      <div>
                        <span className="text-blue-700">Status:</span>
                        <span className={`ml-1 font-medium ${cameraInfo.is_connected ? 'text-green-600' : 'text-red-600'}`}>
                          {cameraInfo.is_connected ? 'Terhubung' : 'Terputus'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Hikvision Presets */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                    <Wifi className="w-4 h-4 mr-2 text-blue-600" />
                    Kamera Hikvision (IP: 192.168.200.64)
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                    {hikvisionPresets.map((camera) => (
                      <button
                        key={camera.id}
                        onClick={() => handleCameraSelect(camera.source)}
                        className={`p-4 border rounded-lg text-left hover:bg-blue-50 transition-colors relative ${
                          cameraInfo?.camera_source === camera.source 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200'
                        }`}
                      >
                        {camera.recommended && (
                          <div className="absolute top-2 right-2">
                            <Star className="w-4 h-4 text-yellow-500 fill-current" />
                          </div>
                        )}
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            {getCameraTypeIcon(camera.type)}
                            <span className="font-medium text-sm">{camera.name}</span>
                          </div>
                          <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(camera.status)}`}>
                            {getStatusText(camera.status)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-600 mb-1">{camera.description}</div>
                        <div className="text-xs text-gray-500 mb-1">Resolusi: {camera.resolution}</div>
                        <div className="text-xs text-gray-400 break-all">{camera.source}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Available Cameras */}
                {availableCameras.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                      <Monitor className="w-4 h-4 mr-2 text-gray-600" />
                      Kamera Lainnya
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {availableCameras.map((camera, index) => (
                        <button
                          key={index}
                          onClick={() => handleCameraSelect(camera.source)}
                          className={`p-4 border rounded-lg text-left hover:bg-blue-50 transition-colors ${
                            cameraInfo?.camera_source === camera.source 
                              ? 'border-blue-500 bg-blue-50' 
                              : 'border-gray-200'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              {getCameraTypeIcon(camera.type)}
                              <span className="font-medium">{camera.name}</span>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(camera.status)}`}>
                              {getStatusText(camera.status)}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500 break-all">{camera.source}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Custom Camera URL */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-3">URL Kamera Kustom</h4>
                  <form onSubmit={handleCustomCameraSubmit} className="flex space-x-2">
                    <input
                      type="text"
                      value={customUrl}
                      onChange={(e) => setCustomUrl(e.target.value)}
                      placeholder="Masukkan URL kamera (http://192.168.1.100:8080/video atau rtsp://...)"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="submit"
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      Gunakan
                    </button>
                  </form>
                  <p className="text-xs text-gray-500 mt-1">
                    Contoh: http://192.168.1.100:8080/video, rtsp://192.168.1.100:554/stream
                  </p>
                </div>

                {/* Camera Properties (only for webcam) */}
                {cameraInfo?.camera_type === 'webcam' && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                      <Sliders className="w-4 h-4 mr-2" />
                      Pengaturan Webcam
                    </h4>
                    <div className="space-y-4">
                      {Object.entries(cameraSettings).map(([property, value]) => (
                        <div key={property}>
                          <div className="flex justify-between items-center mb-2">
                            <label className="text-sm font-medium text-gray-700 capitalize">
                              {property}
                            </label>
                            <span className="text-sm text-gray-500">{value}%</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={value}
                            onChange={(e) => {
                              const newValue = parseInt(e.target.value)
                              setCameraSettings(prev => ({ ...prev, [property]: newValue }))
                            }}
                            onMouseUp={(e) => handleSettingChange(property, parseInt(e.target.value))}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-3">
            <div className="flex justify-end space-x-3">
              <button
                onClick={loadCameraData}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <RefreshCw className="w-4 h-4 inline mr-2" />
                Refresh
              </button>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Selesai
              </button>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
        }

        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3b82f6;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  )
}

export default CameraSettings 