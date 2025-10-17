import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('Error caught by boundary:', error, errorInfo)
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI
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
            maxWidth: '600px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚠️</div>
            <h1 style={{ color: '#dc2626', marginBottom: '16px' }}>
              Terjadi Kesalahan
            </h1>
            <p style={{ color: '#666', marginBottom: '24px' }}>
              Aplikasi mengalami error dan tidak dapat menampilkan konten dengan benar.
            </p>
            
            {this.state.error && (
              <details style={{ 
                textAlign: 'left', 
                backgroundColor: '#f9fafb', 
                padding: '16px', 
                borderRadius: '8px',
                marginBottom: '24px',
                border: '1px solid #e5e7eb'
              }}>
                <summary style={{ cursor: 'pointer', fontWeight: '600' }}>
                  Detail Error (untuk developer)
                </summary>
                <pre style={{ 
                  marginTop: '12px', 
                  fontSize: '12px', 
                  color: '#dc2626',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                onClick={() => window.location.reload()}
                style={{
                  backgroundColor: '#2563eb',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                🔄 Reload Halaman
              </button>
              
              <button
                onClick={() => {
                  localStorage.clear()
                  window.location.reload()
                }}
                style={{
                  backgroundColor: '#dc2626',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                🗑️ Reset & Reload
              </button>
            </div>

            <div style={{ 
              marginTop: '24px', 
              fontSize: '12px', 
              color: '#9ca3af',
              borderTop: '1px solid #e5e7eb',
              paddingTop: '16px'
            }}>
              <p>Jika masalah terus berlanjut, hubungi tim support.</p>
              <p>Sistem Parkir Manless v2.0</p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary 