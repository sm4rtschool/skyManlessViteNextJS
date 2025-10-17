import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Camera, 
  CreditCard, 
  FileText, 
  Settings,
  CarFront,
  Shield
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()

  const menuItems = [
    {
      name: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
      description: 'Beranda sistem'
    },
    {
      name: 'Live Camera',
      icon: Camera,
      path: '/camera',
      description: 'Tampilan kamera langsung'
    },
    {
      name: 'Card Reader',
      icon: CreditCard,
      path: '/card-reader',
      description: 'Pembaca kartu akses'
    },
    {
      name: 'Log Kendaraan',
      icon: FileText,
      path: '/logs',
      description: 'Riwayat kendaraan'
    },
    {
      name: 'Kontrol Gate',
      icon: CarFront,
      path: '/gate',
      description: 'Kontrol gerbang parkir'
    },
    {
      name: 'Pengaturan',
      icon: Settings,
      path: '/settings',
      description: 'Konfigurasi sistem'
    }
  ]

  return (
    <div className="w-64 bg-white shadow-lg border-r border-gray-200">
      {/* Logo/Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-800">Manless Park</h2>
            <p className="text-xs text-gray-500">Sistem Parkir Otomatis</p>
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="mt-6">
        <div className="px-4">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Menu Utama
          </h3>
        </div>
        
        <ul className="space-y-1 px-4">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path || 
                           (item.path === '/dashboard' && location.pathname === '/')
            
            return (
              <li key={item.name}>
                <Link
                  to={item.path}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-200 group ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className={`mr-3 h-5 w-5 ${
                    isActive ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'
                  }`} />
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-gray-400">{item.description}</div>
                  </div>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Status Connection */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Status Koneksi</span>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-600 font-medium">Terhubung</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar 