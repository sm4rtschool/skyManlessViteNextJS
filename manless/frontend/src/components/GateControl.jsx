import React, { useState, useEffect } from 'react'
import { CarFront, Lock, Unlock, AlertTriangle, Settings, Power } from 'lucide-react'

const GateControl = ({ gateStatus, onGateControl }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [currentStatus, setCurrentStatus] = useState('closed')
  const [lastAction, setLastAction] = useState(null)
  const [autoCloseTimer, setAutoCloseTimer] = useState(null)
  const [manualMode, setManualMode] = useState(false)

  useEffect(() => {
    // Simulasi koneksi Arduino
    setTimeout(() => {
      setIsConnected(true)
      console.log('Arduino terhubung')
    }, 1500)
  }, [])

  useEffect(() => {
    if (gateStatus) {
      setCurrentStatus(gateStatus)
    }
  }, [gateStatus])

  const handleGateAction = async (action) => {
    if (!isConnected) {
      console.error('Arduino tidak terhubung')
      return
    }

    setLastAction({
      action,
      timestamp: new Date().toISOString(),
      status: 'processing'
    })

    try {
      if (action === 'open') {
        setCurrentStatus('opening')
        console.log('Membuka gerbang...')
        
        // Simulasi delay membuka gerbang
        setTimeout(() => {
          setCurrentStatus('open')
          console.log('Gerbang berhasil dibuka')
          
          setLastAction(prev => ({ ...prev, status: 'success' }))
          
          // Auto close setelah 10 detik jika tidak manual mode
          if (!manualMode) {
            const timer = setTimeout(() => {
              handleGateAction('close')
            }, 10000)
            setAutoCloseTimer(timer)
          }
        }, 2000)
        
      } else if (action === 'close') {
        // Clear auto close timer
        if (autoCloseTimer) {
          clearTimeout(autoCloseTimer)
          setAutoCloseTimer(null)
        }
        
        setCurrentStatus('closing')
        console.log('Menutup gerbang...')
        
        // Simulasi delay menutup gerbang
        setTimeout(() => {
          setCurrentStatus('closed')
          console.log('Gerbang berhasil ditutup')
          setLastAction(prev => ({ ...prev, status: 'success' }))
        }, 2000)
      }
      
      // Callback ke parent component
      if (onGateControl) {
        onGateControl(action)
      }
      
    } catch (error) {
      console.error(`Gagal ${action === 'open' ? 'membuka' : 'menutup'} gerbang`)
      setLastAction(prev => ({ ...prev, status: 'error' }))
    }
  }

  const getStatusColor = () => {
    const colors = {
      'closed': 'bg-green-50 border-green-200 text-green-800',
      'open': 'bg-yellow-50 border-yellow-200 text-yellow-800',
      'opening': 'bg-blue-50 border-blue-200 text-blue-800',
      'closing': 'bg-blue-50 border-blue-200 text-blue-800',
      'error': 'bg-red-50 border-red-200 text-red-800'
    }
    return colors[currentStatus] || colors.closed
  }

  const getStatusIcon = () => {
    const iconClass = "w-8 h-8"
    switch (currentStatus) {
      case 'closed':
        return <Lock className={`${iconClass} text-green-600`} />
      case 'open':
        return <Unlock className={`${iconClass} text-yellow-600`} />
      case 'opening':
        return <Unlock className={`${iconClass} text-blue-600 animate-pulse`} />
      case 'closing':
        return <Lock className={`${iconClass} text-blue-600 animate-pulse`} />
      case 'error':
        return <AlertTriangle className={`${iconClass} text-red-600`} />
      default:
        return <Lock className={`${iconClass} text-gray-400`} />
    }
  }

  const getStatusText = () => {
    const texts = {
      'closed': 'Tertutup',
      'open': 'Terbuka',
      'opening': 'Sedang Membuka...',
      'closing': 'Sedang Menutup...',
      'error': 'Error'
    }
    return texts[currentStatus] || 'Tidak Diketahui'
  }

  const canOpen = isConnected && (currentStatus === 'closed')
  const canClose = isConnected && (currentStatus === 'open')
  const isProcessing = currentStatus === 'opening' || currentStatus === 'closing'

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <CarFront className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-800">Kontrol Gerbang</h3>
          <div className="flex items-center space-x-2">
            <Power className={`w-4 h-4 ${isConnected ? 'text-green-600' : 'text-red-600'}`} />
            <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
              {isConnected ? 'Arduino Online' : 'Arduino Offline'}
            </span>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={manualMode}
              onChange={(e) => setManualMode(e.target.checked)}
              className="rounded"
            />
            <span className="text-gray-600">Manual Mode</span>
          </label>
          <button className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Gate Status Display */}
      <div className="p-6">
        <div className={`border-2 rounded-lg p-6 text-center transition-all duration-300 ${getStatusColor()}`}>
          <div className="flex flex-col items-center space-y-4">
            {getStatusIcon()}
            <div>
              <h4 className="text-xl font-semibold mb-2">
                Status Gerbang: {getStatusText()}
              </h4>
              <p className="text-sm opacity-75">
                {currentStatus === 'open' && !manualMode && autoCloseTimer ? 
                  'Akan tertutup otomatis dalam 10 detik' :
                  currentStatus === 'closed' ? 'Gerbang siap digunakan' :
                  currentStatus === 'open' ? 'Kendaraan dapat melewati gerbang' :
                  'Sedang memproses...'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="px-6 pb-6">
        <div className="flex space-x-3">
          <button
            onClick={() => handleGateAction('open')}
            disabled={!canOpen || isProcessing}
            className={`flex-1 px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 ${
              canOpen && !isProcessing
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Unlock className="w-5 h-5" />
            <span>Buka Gerbang</span>
          </button>
          
          <button
            onClick={() => handleGateAction('close')}
            disabled={!canClose || isProcessing}
            className={`flex-1 px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 ${
              canClose && !isProcessing
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Lock className="w-5 h-5" />
            <span>Tutup Gerbang</span>
          </button>
        </div>
      </div>

      {/* Last Action Info */}
      {lastAction && (
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Aksi Terakhir:</span>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                lastAction.status === 'success' ? 'bg-green-100 text-green-800' :
                lastAction.status === 'error' ? 'bg-red-100 text-red-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {lastAction.action === 'open' ? 'Buka' : 'Tutup'} - {
                  lastAction.status === 'success' ? 'Berhasil' :
                  lastAction.status === 'error' ? 'Gagal' :
                  'Sedang Proses'
                }
              </span>
              <span className="text-gray-500">
                {new Date(lastAction.timestamp).toLocaleTimeString('id-ID')}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Gate Specifications */}
      <div className="border-t border-gray-200 px-4 pb-4">
        <div className="pt-4 text-sm text-gray-600 space-y-1">
          <div className="flex justify-between">
            <span>Jenis Motor:</span>
            <span>Servo SG90</span>
          </div>
          <div className="flex justify-between">
            <span>Waktu Buka/Tutup:</span>
            <span>2 detik</span>
          </div>
          <div className="flex justify-between">
            <span>Auto Close:</span>
            <span>{manualMode ? 'Dinonaktifkan' : '10 detik'}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GateControl 