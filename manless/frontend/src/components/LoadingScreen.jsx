import React from 'react'
import { gateConfig } from '../services/gateConfig.js'

const LoadingScreen = ({ message = "Loading..." }) => {
  const gateInfo = gateConfig.getGateInfo()
  
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#f5f5f5',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '40px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        textAlign: 'center',
        borderLeft: `6px solid ${gateInfo.color}`
      }}>
        {/* Gate Icon */}
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>
          {gateInfo.icon}
        </div>
        
        {/* Gate Name */}
        <h2 style={{ 
          margin: '0 0 16px 0', 
          color: gateInfo.color,
          fontSize: '24px',
          fontWeight: '600'
        }}>
          {gateInfo.name}
        </h2>
        
        {/* Loading Spinner */}
        <div style={{
          width: '40px',
          height: '40px',
          border: `4px solid ${gateInfo.color}20`,
          borderTop: `4px solid ${gateInfo.color}`,
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 20px auto'
        }}></div>
        
        {/* Loading Message */}
        <p style={{ 
          color: '#666', 
          margin: '0 0 16px 0',
          fontSize: '16px'
        }}>
          {message}
        </p>
        
        {/* Location */}
        <p style={{ 
          color: '#999', 
          margin: 0,
          fontSize: '12px'
        }}>
          📍 {gateInfo.location}
        </p>
      </div>
      
      {/* CSS for spinner animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

export default LoadingScreen 