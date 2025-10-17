import React, { useState, useEffect, useRef } from 'react'
import { FileText, Search, Filter, Download, RefreshCw } from 'lucide-react'
import { apiService } from '../services/api'

const LogViewer = () => {
  const [logs, setLogs] = useState([])
  const [filteredLogs, setFilteredLogs] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [isAutoScroll, setIsAutoScroll] = useState(true)
  const logContainerRef = useRef(null)

  // Load data log dari API
  useEffect(() => {
    const loadLogs = async () => {
      try {
        const response = await apiService.getParkingLogs(50, 0)
        const apiLogs = response.logs.map(log => ({
          id: log.id,
          timestamp: log.timestamp,
          type: log.event_type,
          message: getMessageForType(log.event_type),
          details: log.details || getDetailsForType(log.event_type),
          cardId: log.card_id,
          severity: getSeverityForType(log.event_type)
        }))
        
        setLogs(apiLogs)
        console.log('Logs loaded from API:', apiLogs.length, 'entries')
      } catch (error) {
        console.error('Error loading logs from API:', error)
        // Fallback ke sample data jika API gagal
        generateFallbackLogs()
      }
    }

    const generateFallbackLogs = () => {
      const sampleLogs = [
        {
          id: 1,
          timestamp: new Date(Date.now() - 10000).toISOString(),
          type: 'SYSTEM_STATUS',
          message: 'Sistem parkir dimulai',
          details: 'Inisialisasi berhasil',
          cardId: null,
          severity: 'info'
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 8000).toISOString(),
          type: 'ENTRY',
          message: 'Kendaraan masuk ke area parkir',
          details: 'Sensor mendeteksi kendaraan',
          cardId: 'A1B2C3D4',
          severity: 'success'
        }
      ]
      setLogs(sampleLogs)
    }

    loadLogs()

    // Refresh logs setiap 10 detik
    const interval = setInterval(loadLogs, 10000)
    return () => clearInterval(interval)
  }, [])

  // Helper functions
  const getMessageForType = (type) => {
    const messages = {
      'ENTRY': 'Kendaraan masuk ke area parkir',
      'EXIT': 'Kendaraan keluar dari area parkir',
      'CARD_DETECTED': 'Kartu akses terdeteksi',
      'GATE_OPEN': 'Gerbang dibuka',
      'GATE_CLOSE': 'Gerbang ditutup',
      'SYSTEM_STATUS': 'Status sistem',
      'ERROR': 'Error sistem',
      'CAMERA_CAPTURE': 'Foto kendaraan diambil',
      'VEHICLE_PASSED': 'Kendaraan melewati gerbang'
    }
    return messages[type] || 'Log entry'
  }

  const getDetailsForType = (type) => {
    const details = {
      'ENTRY': 'Kendaraan berhasil masuk area parkir',
      'EXIT': 'Kendaraan berhasil keluar dari area parkir',
      'CARD_DETECTED': 'Kartu akses valid dan terverifikasi',
      'GATE_OPEN': 'Gerbang berhasil dibuka',
      'GATE_CLOSE': 'Gerbang berhasil ditutup',
      'SYSTEM_STATUS': 'Sistem berfungsi normal',
      'ERROR': 'Terjadi error pada sistem',
      'CAMERA_CAPTURE': `Gambar disimpan: capture_${Date.now()}.jpg`,
      'VEHICLE_PASSED': 'Kendaraan telah melewati sensor'
    }
    return details[type] || 'Detail log'
  }

  const getSeverityForType = (type) => {
    const severities = {
      'ENTRY': 'success',
      'EXIT': 'success',
      'CARD_DETECTED': 'success',
      'GATE_OPEN': 'info',
      'GATE_CLOSE': 'info',
      'SYSTEM_STATUS': 'info',
      'ERROR': 'error',
      'CAMERA_CAPTURE': 'info',
      'VEHICLE_PASSED': 'success'
    }
    return severities[type] || 'info'
  }

  // Filter dan search logs
  useEffect(() => {
    let filtered = logs

    // Filter by type
    if (filterType !== 'all') {
      filtered = filtered.filter(log => log.type === filterType)
    }

    // Search
    if (searchTerm) {
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (log.cardId && log.cardId.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }

    setFilteredLogs(filtered)
  }, [logs, filterType, searchTerm])

  // Auto scroll to bottom
  useEffect(() => {
    if (isAutoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [filteredLogs, isAutoScroll])

  const getSeverityColor = (severity) => {
    const colors = {
      'info': 'bg-blue-50 border-blue-200 text-blue-800',
      'success': 'bg-green-50 border-green-200 text-green-800',
      'warning': 'bg-yellow-50 border-yellow-200 text-yellow-800',
      'error': 'bg-red-50 border-red-200 text-red-800'
    }
    return colors[severity] || colors.info
  }

  const getSeverityDot = (severity) => {
    const colors = {
      'info': 'bg-blue-500',
      'success': 'bg-green-500',
      'warning': 'bg-yellow-500',
      'error': 'bg-red-500'
    }
    return colors[severity] || colors.info
  }

  const exportLogs = () => {
    const csv = [
      ['Timestamp', 'Type', 'Message', 'Details', 'Card ID', 'Severity'],
      ...filteredLogs.map(log => [
        new Date(log.timestamp).toLocaleString('id-ID'),
        log.type,
        log.message,
        log.details,
        log.cardId || '',
        log.severity
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `parking_logs_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <FileText className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-800">Log Aktivitas</h3>
          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
            {filteredLogs.length} entries
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={exportLogs}
            className="px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-1"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          <button
            onClick={() => setIsAutoScroll(!isAutoScroll)}
            className={`px-3 py-2 text-sm rounded-lg transition-colors flex items-center space-x-1 ${
              isAutoScroll ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            <RefreshCw className="w-4 h-4" />
            <span>Auto Scroll</span>
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Cari dalam log..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-600" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Semua</option>
              <option value="VEHICLE_ARRIVAL">Kedatangan</option>
              <option value="CARD_DETECTED">Kartu</option>
              <option value="GATE_OPENING">Buka Gate</option>
              <option value="GATE_CLOSING">Tutup Gate</option>
              <option value="VEHICLE_PASSED">Lewat</option>
              <option value="CAMERA_CAPTURE">Kamera</option>
              <option value="SYSTEM_STATUS">Sistem</option>
              <option value="ERROR">Error</option>
            </select>
          </div>
        </div>
      </div>

      {/* Log Content */}
      <div 
        ref={logContainerRef}
        className="h-96 overflow-y-auto p-4 space-y-2"
        onScroll={(e) => {
          const { scrollTop, scrollHeight, clientHeight } = e.target
          setIsAutoScroll(scrollTop + clientHeight >= scrollHeight - 10)
        }}
      >
        {filteredLogs.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500">Tidak ada log yang ditemukan</p>
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className={`p-3 rounded-lg border ${getSeverityColor(log.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className={`w-2 h-2 rounded-full mt-2 ${getSeverityDot(log.severity)}`}></div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-xs font-mono bg-gray-200 px-2 py-1 rounded">
                        {log.type}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(log.timestamp).toLocaleString('id-ID')}
                      </span>
                      {log.cardId && (
                        <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                          {log.cardId}
                        </span>
                      )}
                    </div>
                    <p className="font-medium text-gray-900 mb-1">{log.message}</p>
                    <p className="text-sm text-gray-600">{log.details}</p>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default LogViewer 