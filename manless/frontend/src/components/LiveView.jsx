import React, { useState, useEffect, useRef } from 'react'
import { Card } from './ui/card'

const LiveView = ({ 
  variant = 'default', // 'default' atau 'dark'
  showCard = true,
  className = ''
}) => {
  const videoRef = useRef(null)
  const [cameraConnected, setCameraConnected] = useState(false)
  const [cameraError, setCameraError] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [debugInfo, setDebugInfo] = useState('')
  const [useFallback, setUseFallback] = useState(false)
  const [videoElementReady, setVideoElementReady] = useState(false)
  const [stream, setStream] = useState(null)

  // DISABLED: IP Camera configurations (untuk sementara)
  // const DAHUA_IP = '10.5.50.129'
  // const DAHUA_USERNAME = 'admin'
  // const DAHUA_PASSWORD = 'SKYUPH@2025'

  useEffect(() => {
    // Initialize webcam laptop
    const initializeWebcam = async () => {
      try {
        setIsLoading(true)
        setDebugInfo('🎥 Checking webcam availability...')
        console.log('🎥 Initializing laptop webcam...')
        
        // Check if getUserMedia is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error('getUserMedia tidak didukung di browser ini')
        }

        setDebugInfo('🎥 Requesting camera permission...')
        
        // Try different video constraints
        const constraints = [
          { 
            video: { 
              width: { ideal: 640 },
              height: { ideal: 480 },
              facingMode: 'environment'
            } 
          },
          { 
            video: { 
              width: { ideal: 1280 },
              height: { ideal: 720 }
            } 
          },
          { 
            video: true 
          }
        ]

        let mediaStream = null
        let constraintIndex = 0

        while (!mediaStream && constraintIndex < constraints.length) {
          try {
            setDebugInfo(`🎥 Trying constraint ${constraintIndex + 1}/${constraints.length}...`)
            console.log(`Trying constraint:`, constraints[constraintIndex])
            mediaStream = await navigator.mediaDevices.getUserMedia(constraints[constraintIndex])
            break
          } catch (constraintError) {
            console.warn(`Constraint ${constraintIndex + 1} failed:`, constraintError)
            constraintIndex++
          }
        }

        if (!mediaStream) {
          throw new Error('Tidak dapat mengakses webcam dengan semua konfigurasi')
        }

        setDebugInfo('🎥 Stream obtained, waiting for video element...')
        setStream(mediaStream)
        setCameraConnected(true)
        setCameraError(null)
        
        // Log video track info
        const videoTrack = mediaStream.getVideoTracks()[0]
        if (videoTrack) {
          console.log('📹 Video track info:', {
            label: videoTrack.label,
            enabled: videoTrack.enabled,
            readyState: videoTrack.readyState,
            settings: videoTrack.getSettings()
          })
        }
        
      } catch (error) {
        console.error('❌ Error accessing webcam:', error)
        setCameraConnected(false)
        setCameraError(`Error: ${error.message}`)
        setDebugInfo(`❌ ${error.message}`)
        
        // Auto-enable fallback if webcam fails
        if (error.message.includes('permission') || error.message.includes('denied')) {
          setUseFallback(true)
          setDebugInfo('🔄 Switching to fallback mode...')
        }
      } finally {
        setIsLoading(false)
      }
    }

    // Delay initialization to ensure component is fully mounted
    const initTimeout = setTimeout(() => {
      initializeWebcam()
    }, 100)

    // Cleanup on unmount
    return () => {
      clearTimeout(initTimeout)
      if (stream) {
        const tracks = stream.getTracks()
        tracks.forEach(track => {
          console.log('🛑 Stopping track:', track.label)
          track.stop()
        })
      }
    }
  }, [])

  // Set stream to video element when both are ready
  useEffect(() => {
    if (videoRef.current && stream && videoElementReady) {
      console.log('🎥 Setting stream to video element')
      setDebugInfo('🎥 Setting stream to video element...')
      videoRef.current.srcObject = stream
      setDebugInfo('✅ Webcam connected successfully')
      console.log('✅ Webcam connected successfully')
    }
  }, [videoRef.current, stream, videoElementReady])

  // Monitor videoRef changes
  useEffect(() => {
    if (videoRef.current) {
      console.log('🎥 Video element mounted:', videoRef.current)
      setDebugInfo('🎥 Video element ready')
      setVideoElementReady(true)
    }
  }, [videoRef.current])

  const handleRetry = () => {
    setIsLoading(true)
    setCameraError(null)
    setDebugInfo('🔄 Retrying webcam connection...')
    setUseFallback(false)
    
    // Stop existing stream first
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject
      const tracks = stream.getTracks()
      tracks.forEach(track => track.stop())
    }
    
    // Re-run initialization
    setTimeout(() => {
      window.location.reload()
    }, 500)
  }

  const handleVideoLoad = () => {
    console.log('✅ Video loaded successfully')
    console.log('📹 Video element:', videoRef.current)
    console.log('📹 Video readyState:', videoRef.current?.readyState)
    console.log('📹 Video srcObject:', videoRef.current?.srcObject)
    setDebugInfo('✅ Video stream active')
  }

  const handleVideoError = (error) => {
    console.error('❌ Video error:', error)
    console.error('❌ Video element:', videoRef.current)
    console.error('❌ Video srcObject:', videoRef.current?.srcObject)
    setCameraError('Error loading video stream')
    setDebugInfo('❌ Video stream error')
  }

  const enableFallback = () => {
    setUseFallback(true)
    setCameraError(null)
    setDebugInfo('🔄 Using fallback mode')
  }

  // Fallback content when webcam fails
  if (useFallback) {
    const fallbackContent = (
      <div className="flex justify-between items-center mb-4">
        <h3 className={`text-lg font-semibold ${variant === 'dark' ? 'text-white' : 'text-gray-900'}`}>
          Live Camera View
        </h3>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <span className={`text-sm ${variant === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>Fallback Mode</span>
        </div>
      </div>
    )

    const fallbackBody = (
      <div className="relative bg-gray-100 rounded-lg overflow-hidden" style={{ height: '400px' }}>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-gray-600">
            <div className="text-6xl mb-4">📷</div>
            <p className="text-lg mb-2">Camera Unavailable</p>
            <p className="text-sm text-gray-500 mb-4">
              Webcam tidak dapat diakses. Silakan cek permission browser.
            </p>
            <div className="space-x-2">
              <button 
                onClick={handleRetry}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Retry Webcam
              </button>
              <button 
                onClick={() => setUseFallback(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    )

    const fallbackFooter = (
      <div className="mt-4 text-sm text-gray-600">
        <p>📹 Source: Fallback Mode</p>
        <p>🔗 Status: Camera Permission Required</p>
        <p>📍 Resolution: N/A</p>
        <p>🐛 Debug: {debugInfo}</p>
      </div>
    )

    if (showCard) {
      return (
        <Card className={`p-6 ${className}`}>
          {fallbackContent}
          {fallbackBody}
          {fallbackFooter}
        </Card>
      )
    } else {
      return (
        <div className={className}>
          {fallbackBody}
        </div>
      )
    }
  }

  const mainContent = (
    <div className="flex justify-between items-center mb-4">
      <h3 className={`text-lg font-semibold ${variant === 'dark' ? 'text-white' : 'text-gray-900'}`}>
        Live Camera View
      </h3>
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${
          cameraConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
        }`}></div>
        <span className={`text-sm ${variant === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
          {cameraConnected ? 'Webcam Connected' : 'Webcam Disconnected'}
        </span>
      </div>
    </div>
  )

  const videoContainer = (
    <div className="relative w-full h-full bg-black rounded-lg overflow-hidden shadow-2xl border-2 border-gray-700 hover:border-blue-500 transition-all duration-300">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
          <div className="text-center text-white">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
            <p className="mb-2">Connecting to webcam...</p>
            <p className="text-xs text-gray-300">{debugInfo}</p>
          </div>
        </div>
      )}

      {cameraError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 text-center">
          <div className="text-white">
            <div className="text-6xl mb-4">📷</div>
            <p className="text-lg mb-2">Camera Error</p>
            <p className="text-sm text-gray-300 mb-2">{cameraError}</p>
            <p className="text-xs text-gray-400 mb-4">{debugInfo}</p>
            <div className="space-x-2">
              <button 
                onClick={handleRetry}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Retry Connection
              </button>
              <button 
                onClick={enableFallback}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors"
              >
                Use Fallback
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Video element for dark variant */}
      <video 
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-cover rounded-lg"
        onLoadedMetadata={handleVideoLoad}
        onError={handleVideoError}
        onCanPlay={() => {
          console.log('✅ Video can play')
          console.log('📹 Video element in onCanPlay:', videoRef.current)
          setDebugInfo('✅ Video ready to play')
        }}
        onLoadStart={() => {
          console.log('🔄 Video load started')
          setDebugInfo('🔄 Video loading...')
        }}
        onLoadedData={() => {
          console.log('📹 Video data loaded')
          setDebugInfo('📹 Video data loaded')
        }}
        onPlay={() => {
          console.log('▶️ Video started playing')
          setDebugInfo('▶️ Video playing')
        }}
        style={{ 
          display: stream && !isLoading ? 'block' : 'none',
          objectFit: 'cover',
          borderRadius: '8px'
        }}
      />

      {/* Status overlay for dark variant */}
      <div className="absolute bottom-4 left-4 bg-black bg-opacity-70 text-white px-3 py-1 rounded-lg text-sm font-medium backdrop-blur-sm border border-gray-600">
        {isLoading ? 'Connecting...' : 
         cameraConnected ? 'LIVE - Webcam' : cameraError}
      </div>

      {/* Camera info overlay for dark variant */}
      <div className="absolute top-4 right-4 bg-black bg-opacity-70 text-white px-3 py-1 rounded-lg text-xs backdrop-blur-sm border border-gray-600">
        📹 Webcam Mode
      </div>

      {/* Live indicator for dark variant */}
      {cameraConnected && !isLoading && (
        <div className="absolute top-4 left-4 flex items-center space-x-2">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-white bg-red-500 bg-opacity-80 px-2 py-1 rounded-full font-medium">LIVE</span>
        </div>
      )}

      {/* Corner indicators */}
      <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-blue-500 rounded-tl-lg"></div>
      <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-blue-500 rounded-tr-lg"></div>
      <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-blue-500 rounded-bl-lg"></div>
      <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-blue-500 rounded-br-lg"></div>

      {/* Gradient overlay for better text readability */}
      <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-30 pointer-events-none"></div>
    </div>
  )

  const footerInfo = (
    <div className={`mt-4 text-sm ${variant === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
      <p>📹 Source: Laptop Webcam</p>
      <p>🔗 Status: {cameraConnected ? 'Connected' : 'Disconnected'}</p>
      <p>📍 Resolution: 640x480 (ideal)</p>
      <p>🐛 Debug: {debugInfo}</p>
    </div>
  )

  if (showCard) {
    return (
      <Card className={`p-6 ${className}`}>
        {mainContent}
        {videoContainer}
        {footerInfo}
      </Card>
    )
  } else {
    return (
      <div className={`w-full h-full ${className}`}>
        <div className="relative w-full h-full bg-black rounded-lg overflow-hidden shadow-2xl border-2 border-gray-700 hover:border-blue-500 transition-all duration-300">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
              <div className="text-center text-white">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
                <p className="mb-2">Connecting to webcam...</p>
                <p className="text-xs text-gray-300">{debugInfo}</p>
              </div>
            </div>
          )}

          {cameraError && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 text-center">
              <div className="text-white">
                <div className="text-6xl mb-4">📷</div>
                <p className="text-lg mb-2">Camera Error</p>
                <p className="text-sm text-gray-300 mb-2">{cameraError}</p>
                <p className="text-xs text-gray-400 mb-4">{debugInfo}</p>
                <div className="space-x-2">
                  <button 
                    onClick={handleRetry}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                  >
                    Retry Connection
                  </button>
                  <button 
                    onClick={enableFallback}
                    className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors"
                  >
                    Use Fallback
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Video element for dark variant */}
          <video 
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover rounded-lg"
            onLoadedMetadata={handleVideoLoad}
            onError={handleVideoError}
            onCanPlay={() => {
              console.log('✅ Video can play')
              console.log('📹 Video element in onCanPlay:', videoRef.current)
              setDebugInfo('✅ Video ready to play')
            }}
            onLoadStart={() => {
              console.log('🔄 Video load started')
              setDebugInfo('🔄 Video loading...')
            }}
            onLoadedData={() => {
              console.log('📹 Video data loaded')
              setDebugInfo('📹 Video data loaded')
            }}
            onPlay={() => {
              console.log('▶️ Video started playing')
              setDebugInfo('▶️ Video playing')
            }}
            style={{ 
              display: stream && !isLoading ? 'block' : 'none',
              objectFit: 'cover',
              borderRadius: '8px'
            }}
          />

          {/* Status overlay for dark variant */}
          <div className="absolute bottom-4 left-4 bg-black bg-opacity-70 text-white px-3 py-1 rounded-lg text-sm font-medium backdrop-blur-sm border border-gray-600">
            {isLoading ? 'Connecting...' : 
             cameraConnected ? 'LIVE - Webcam' : cameraError}
          </div>

          {/* Camera info overlay for dark variant */}
          <div className="absolute top-4 right-4 bg-black bg-opacity-70 text-white px-3 py-1 rounded-lg text-xs backdrop-blur-sm border border-gray-600">
            📹 Webcam Mode
          </div>

          {/* Live indicator for dark variant */}
          {cameraConnected && !isLoading && (
            <div className="absolute top-4 left-4 flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-white bg-red-500 bg-opacity-80 px-2 py-1 rounded-full font-medium">LIVE</span>
            </div>
          )}

          {/* Corner indicators */}
          <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-blue-500 rounded-tl-lg"></div>
          <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-blue-500 rounded-tr-lg"></div>
          <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-blue-500 rounded-bl-lg"></div>
          <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-blue-500 rounded-br-lg"></div>

          {/* Gradient overlay for better text readability */}
          <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-30 pointer-events-none"></div>
        </div>
      </div>
    )
  }
}

export default LiveView 