import React, { useState, useRef } from 'react'
import { Camera, CheckCircle, XCircle, RefreshCw, Video } from 'lucide-react'

const CameraTest = () => {
  // DISABLED: Camera Dahua Configuration (untuk sementara)
  // const DAHUA_IP = '10.5.50.129'
  // const DAHUA_USERNAME = 'admin'
  // const DAHUA_PASSWORD = 'SKYUPH@2025'
  // const DAHUA_SNAPSHOT_URL = `http://${DAHUA_USERNAME}:${DAHUA_PASSWORD}@${DAHUA_IP}/cgi-bin/snapshot.cgi`

  const [testResult, setTestResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)
  const [webcamTestResult, setWebcamTestResult] = useState(null)
  const [isWebcamLoading, setIsWebcamLoading] = useState(false)
  const videoRef = useRef(null)

  const testCamera = () => {
    setIsLoading(true)
    setTestResult(null)
    setImageLoaded(false)

    // DISABLED: IP Camera test (untuk sementara)
    setTimeout(() => {
      console.log('⚠️ Camera Dahua test disabled')
      setTestResult({
        success: false,
        message: `IP Camera testing disabled untuk sementara`,
        timestamp: new Date()
      })
      setIsLoading(false)
    }, 1000)
  }

  const testWebcam = async () => {
    setIsWebcamLoading(true)
    setWebcamTestResult(null)
    
    try {
      console.log('🎥 Testing webcam access...')
      
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('getUserMedia tidak didukung di browser ini')
      }

      // Get available devices
      const devices = await navigator.mediaDevices.enumerateDevices()
      const videoDevices = devices.filter(device => device.kind === 'videoinput')
      
      console.log('📹 Available video devices:', videoDevices)

      // Try to get user media
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }

      setWebcamTestResult({
        success: true,
        message: `Webcam berhasil diakses. ${videoDevices.length} device(s) tersedia.`,
        devices: videoDevices,
        timestamp: new Date()
      })

      console.log('✅ Webcam test successful')
      
    } catch (error) {
      console.error('❌ Webcam test failed:', error)
      setWebcamTestResult({
        success: false,
        message: `Error: ${error.message}`,
        timestamp: new Date()
      })
    } finally {
      setIsWebcamLoading(false)
    }
  }

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject
      const tracks = stream.getTracks()
      tracks.forEach(track => track.stop())
      videoRef.current.srcObject = null
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <div className="flex items-center space-x-3 mb-4">
        <Camera className="w-6 h-6 text-gray-600" />
        <h3 className="text-lg font-semibold text-gray-800">Test Camera</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Webcam Test */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-700">Test Webcam Laptop</h4>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <h5 className="font-medium text-gray-700 mb-2">Status Webcam</h5>
            <div className="text-sm text-gray-600 space-y-1">
              <div><span className="font-medium">Browser:</span> {navigator.userAgent.includes('Chrome') ? 'Chrome' : navigator.userAgent.includes('Firefox') ? 'Firefox' : 'Other'}</div>
              <div><span className="font-medium">getUserMedia:</span> {navigator.mediaDevices && navigator.mediaDevices.getUserMedia ? '✅ Supported' : '❌ Not Supported'}</div>
              <div><span className="font-medium">HTTPS:</span> {window.location.protocol === 'https:' ? '✅ Secure' : '⚠️ HTTP (may need HTTPS)'}</div>
            </div>
          </div>

          <div className="space-y-2">
            <button
              onClick={testWebcam}
              disabled={isWebcamLoading}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isWebcamLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Testing Webcam...</span>
                </>
              ) : (
                <>
                  <Video className="w-4 h-4" />
                  <span>Test Webcam Access</span>
                </>
              )}
            </button>

            {webcamTestResult && (
              <button
                onClick={stopWebcam}
                className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Stop Webcam
              </button>
            )}
          </div>

          {webcamTestResult && (
            <div className={`rounded-lg p-4 ${webcamTestResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className="flex items-center space-x-2 mb-2">
                {webcamTestResult.success ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-600" />
                )}
                <span className={`font-medium ${webcamTestResult.success ? 'text-green-800' : 'text-red-800'}`}>
                  {webcamTestResult.success ? 'Webcam Test Berhasil' : 'Webcam Test Gagal'}
                </span>
              </div>
              <p className={`text-sm ${webcamTestResult.success ? 'text-green-700' : 'text-red-700'}`}>
                {webcamTestResult.message}
              </p>
              {webcamTestResult.devices && (
                <div className="mt-2">
                  <p className="text-xs text-gray-600">Available devices:</p>
                  {webcamTestResult.devices.map((device, index) => (
                    <p key={index} className="text-xs text-gray-500">• {device.label || `Camera ${index + 1}`}</p>
                  ))}
                </div>
              )}
              <p className="text-xs text-gray-500 mt-1">
                {webcamTestResult.timestamp.toLocaleString('id-ID')}
              </p>
            </div>
          )}

          {/* Webcam Preview */}
          {webcamTestResult && webcamTestResult.success && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h5 className="font-medium text-gray-700 mb-2">Webcam Preview</h5>
              <div className="relative bg-black rounded overflow-hidden" style={{ height: '200px' }}>
                <video 
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          )}
        </div>

        {/* IP Camera Test */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-700">Test Camera Dahua (IP)</h4>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <h5 className="font-medium text-gray-700 mb-2">Konfigurasi Camera</h5>
            <div className="text-sm text-gray-600 space-y-1">
              <div><span className="font-medium">IP:</span> DISABLED</div>
              <div><span className="font-medium">Username:</span> DISABLED</div>
              <div><span className="font-medium">Password:</span> DISABLED</div>
              <div><span className="font-medium">URL:</span> IP Camera disabled untuk sementara</div>
            </div>
          </div>

          <button
            onClick={testCamera}
            disabled={isLoading}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Testing...</span>
              </>
            ) : (
              <>
                <Camera className="w-4 h-4" />
                <span>Test Koneksi Camera</span>
              </>
            )}
          </button>

          {testResult && (
            <div className={`rounded-lg p-4 ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className="flex items-center space-x-2 mb-2">
                {testResult.success ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-600" />
                )}
                <span className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
                  {testResult.success ? 'Test Berhasil' : 'Test Gagal'}
                </span>
              </div>
              <p className={`text-sm ${testResult.success ? 'text-green-700' : 'text-red-700'}`}>
                {testResult.message}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {testResult.timestamp.toLocaleString('id-ID')}
              </p>
            </div>
          )}

          {/* DISABLED: Camera Preview (untuk sementara) */}
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <h5 className="font-medium text-gray-700 mb-2">Preview Camera</h5>
            <div className="text-gray-500">
              <div className="text-4xl mb-2">📷</div>
              <p className="text-sm">IP Camera Preview DISABLED</p>
              <p className="text-xs">untuk sementara</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CameraTest 