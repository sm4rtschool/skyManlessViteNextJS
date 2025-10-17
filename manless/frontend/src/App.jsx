import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { gateConfig } from './services/gateConfig.js'
import Dashboard from './pages/Dashboard'
import Sidebar from './components/Sidebar'
import ErrorBoundary from './components/ErrorBoundary'

function App() {
  // Check if this is gate-specific mode (kiosk mode)
  const isGateSpecific = gateConfig.isGateSpecific()
  
  if (isGateSpecific) {
    // Gate-specific mode - no sidebar, full screen dashboard
    return (
      <ErrorBoundary>
        <Router>
          <div className="min-h-screen bg-gray-100">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </div>
        </Router>
      </ErrorBoundary>
    )
  }

  // Control center mode - with sidebar and header
  return (
    <ErrorBoundary>
      <Router>
        <div className="flex h-screen bg-gray-100">
          {/* Sidebar */}
          <Sidebar />
          
          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-800">
                  {gateConfig.getDashboardTitle()}
                </h1>
                <div className="flex items-center space-x-2">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-600">Online</span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date().toLocaleString('id-ID')}
                  </div>
                </div>
              </div>
            </header>
            
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </ErrorBoundary>
  )
}

export default App
