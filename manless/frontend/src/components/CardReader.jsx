import React, { useState, useEffect } from 'react'
import { CreditCard, Check, X, AlertCircle, Wifi, WifiOff } from 'lucide-react'

const CardReader = () => {
  const [isConnected, setIsConnected] = useState(false)
  const [currentCard, setCurrentCard] = useState(null)
  const [cardHistory, setCardHistory] = useState([])
  const [readerStatus, setReaderStatus] = useState('idle') // idle, reading, validating, success, error

  useEffect(() => {
    // Simulasi koneksi ke card reader
    const initCardReader = () => {
      // Simulasi delay koneksi
      setTimeout(() => {
        setIsConnected(true)
        console.log('Card reader terhubung')
      }, 2000)
    }

    initCardReader()

    // Simulasi deteksi kartu otomatis
    const interval = setInterval(() => {
      if (Math.random() < 0.1) { // 10% chance setiap 3 detik
        simulateCardDetection()
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const simulateCardDetection = () => {
    const cardIds = ['A1B2C3D4', 'E5F6G7H8', 'I9J0K1L2', 'M3N4O5P6']
    const randomCard = cardIds[Math.floor(Math.random() * cardIds.length)]
    const isValid = Math.random() > 0.2 // 80% valid cards
    
    setReaderStatus('reading')
    
    setTimeout(() => {
      setReaderStatus('validating')
      
      setTimeout(() => {
        const cardData = {
          id: randomCard,
          timestamp: new Date().toISOString(),
          isValid,
          owner: isValid ? 'John Doe' : 'Unknown',
          vehicleType: isValid ? 'Sedan' : null,
          accessLevel: isValid ? 'Standard' : null
        }
        
        setCurrentCard(cardData)
        setCardHistory(prev => [cardData, ...prev.slice(0, 9)]) // Keep last 10
        setReaderStatus(isValid ? 'success' : 'error')
        
        if (isValid) {
          console.log(`Kartu valid: ${cardData.id}`)
        } else {
          console.error(`Kartu tidak valid: ${cardData.id}`)
        }
        
        // Reset setelah 5 detik
        setTimeout(() => {
          setReaderStatus('idle')
          setCurrentCard(null)
        }, 5000)
      }, 1500)
    }, 1000)
  }

  const getStatusColor = () => {
    const colors = {
      'idle': 'border-gray-300 bg-gray-50',
      'reading': 'border-blue-300 bg-blue-50',
      'validating': 'border-yellow-300 bg-yellow-50',
      'success': 'border-green-300 bg-green-50',
      'error': 'border-red-300 bg-red-50'
    }
    return colors[readerStatus] || colors.idle
  }

  const getStatusIcon = () => {
    const iconClass = "w-8 h-8"
    switch (readerStatus) {
      case 'reading':
        return <CreditCard className={`${iconClass} text-blue-600 animate-pulse`} />
      case 'validating':
        return <AlertCircle className={`${iconClass} text-yellow-600 animate-spin`} />
      case 'success':
        return <Check className={`${iconClass} text-green-600`} />
      case 'error':
        return <X className={`${iconClass} text-red-600`} />
      default:
        return <CreditCard className={`${iconClass} text-gray-400`} />
    }
  }

  const getStatusText = () => {
    const texts = {
      'idle': 'Menunggu kartu...',
      'reading': 'Membaca kartu...',
      'validating': 'Memvalidasi...',
      'success': 'Kartu valid!',
      'error': 'Kartu tidak valid!'
    }
    return texts[readerStatus] || 'Tidak diketahui'
  }

  const testCardRead = () => {
    if (readerStatus !== 'idle') return
    simulateCardDetection()
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <CreditCard className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-800">Card Reader</h3>
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <Wifi className="w-4 h-4 text-green-600" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-600" />
            )}
            <span className={`text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
              {isConnected ? 'Terhubung' : 'Terputus'}
            </span>
          </div>
        </div>
        
        <button
          onClick={testCardRead}
          disabled={!isConnected || readerStatus !== 'idle'}
          className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          Test Read
        </button>
      </div>

      {/* Card Reader Area */}
      <div className="p-6">
        <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${getStatusColor()}`}>
          <div className="flex flex-col items-center space-y-4">
            {getStatusIcon()}
            <div>
              <p className="text-lg font-medium text-gray-800 mb-2">
                {getStatusText()}
              </p>
              {currentCard && (
                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>Card ID:</strong> {currentCard.id}</p>
                  <p><strong>Pemilik:</strong> {currentCard.owner}</p>
                  {currentCard.isValid && (
                    <>
                      <p><strong>Jenis Kendaraan:</strong> {currentCard.vehicleType}</p>
                      <p><strong>Level Akses:</strong> {currentCard.accessLevel}</p>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Card History */}
      {cardHistory.length > 0 && (
        <div className="border-t border-gray-200">
          <div className="p-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Riwayat Kartu</h4>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {cardHistory.map((card, index) => (
                <div
                  key={`${card.id}-${card.timestamp}`}
                  className={`flex items-center justify-between p-2 rounded text-sm ${
                    card.isValid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    {card.isValid ? (
                      <Check className="w-4 h-4 text-green-600" />
                    ) : (
                      <X className="w-4 h-4 text-red-600" />
                    )}
                    <span className="font-mono">{card.id}</span>
                    <span className="text-gray-600">{card.owner}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(card.timestamp).toLocaleTimeString('id-ID')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Reader Status */}
      <div className="px-4 pb-4">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>Protocol: ISO 14443-A</span>
            <span>Frequency: 13.56 MHz</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>Status:</span>
            <span className={`font-medium ${
              readerStatus === 'success' ? 'text-green-600' :
              readerStatus === 'error' ? 'text-red-600' :
              readerStatus === 'reading' || readerStatus === 'validating' ? 'text-blue-600' :
              'text-gray-600'
            }`}>
              {getStatusText()}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CardReader 