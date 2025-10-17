import React, { useState, useEffect } from 'react'
import { gateConfig } from '../services/gateConfig.js'

const GateSelector = ({ showSelector = true, className = "" }) => {
  const [currentGate, setCurrentGate] = useState(gateConfig.getCurrentGate())
  const [gateInfo, setGateInfo] = useState(gateConfig.getGateInfo())

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

  const handleGateChange = (newGateId) => {
    gateConfig.setCurrentGate(newGateId)
  }

  const allGates = gateConfig.getAllGates()

  if (!showSelector) {
    // Mode info only - untuk menampilkan gate saat ini
    return (
      <div className={`gate-info ${className}`}>
        <div 
          className="gate-badge"
          style={{ 
            backgroundColor: gateInfo.color,
            color: 'white',
            padding: '8px 16px',
            borderRadius: '20px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            fontWeight: '600'
          }}
        >
          <span>{gateInfo.icon}</span>
          <span>{gateInfo.name}</span>
          {gateInfo.type !== 'monitoring' && (
            <span className="gate-type">({gateInfo.type})</span>
          )}
        </div>
        <div className="gate-location" style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
          📍 {gateInfo.location}
        </div>
      </div>
    )
  }

  // Mode selector - untuk control center
  return (
    <div className={`gate-selector ${className}`}>
      <div className="gate-selector-header">
        <h3>🚪 Pilih Gate</h3>
        <p>Pilih gate untuk monitoring atau pilih "Semua Gate" untuk monitoring terpusat</p>
      </div>

      <div className="gate-options">
        {Object.values(allGates).map((gate) => (
          <div
            key={gate.id}
            className={`gate-option ${currentGate === gate.id ? 'active' : ''}`}
            onClick={() => handleGateChange(gate.id)}
            style={{
              border: `2px solid ${currentGate === gate.id ? gate.color : '#ddd'}`,
              backgroundColor: currentGate === gate.id ? `${gate.color}20` : 'white',
              borderRadius: '12px',
              padding: '16px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              marginBottom: '12px'
            }}
          >
            <div className="gate-option-header">
              <span className="gate-icon" style={{ fontSize: '24px' }}>
                {gate.icon}
              </span>
              <div className="gate-details">
                <h4 style={{ margin: '0 0 4px 0', color: gate.color }}>
                  {gate.name}
                </h4>
                <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>
                  📍 {gate.location}
                </p>
                {gate.port && (
                  <p style={{ margin: 0, fontSize: '11px', color: '#999' }}>
                    🔗 Port {gate.port}
                  </p>
                )}
              </div>
            </div>
            
            {gate.type !== 'monitoring' && (
              <div className="gate-features" style={{ marginTop: '8px', fontSize: '11px' }}>
                <span style={{ 
                  backgroundColor: gate.color, 
                  color: 'white', 
                  padding: '2px 8px', 
                  borderRadius: '10px',
                  marginRight: '4px'
                }}>
                  {gate.type}
                </span>
                {gate.id === 'gate_in' && (
                  <>
                    <span>📹 Camera</span>
                    <span>💳 Card Reader</span>
                    <span>🚧 Gate Control</span>
                  </>
                )}
                {gate.id === 'gate_out' && (
                  <>
                    <span>📹 Camera</span>
                    <span>💳 Card Reader</span>
                    <span>💰 Payment</span>
                    <span>🧾 Receipt</span>
                  </>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="current-selection">
        <h4>Gateway Terpilih:</h4>
        <div className="selected-gate" style={{ 
          padding: '12px', 
          backgroundColor: `${gateInfo.color}10`,
          border: `1px solid ${gateInfo.color}`,
          borderRadius: '8px',
          marginTop: '8px'
        }}>
          <span style={{ fontSize: '18px' }}>{gateInfo.icon}</span>
          <span style={{ fontWeight: '600', marginLeft: '8px' }}>{gateInfo.name}</span>
          <span style={{ fontSize: '12px', color: '#666', marginLeft: '8px' }}>
            - {gateInfo.location}
          </span>
        </div>
      </div>

      <div className="auto-run-info" style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
        <h4>🖥️ Auto-Run URLs untuk Monitor Kiosk:</h4>
        <div className="url-list" style={{ fontSize: '12px', fontFamily: 'monospace' }}>
          <div>Gate IN: <code>?gate=gate_in</code></div>
          <div>Gate OUT: <code>?gate=gate_out</code></div>
          <div>Monitoring: <code>?gate=all</code></div>
        </div>
      </div>
    </div>
  )
}

export default GateSelector 