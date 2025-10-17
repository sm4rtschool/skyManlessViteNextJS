# Frontend Sistem Parkir Manless

Frontend React untuk sistem parkir otomatis dengan fitur real-time monitoring, kontrol gerbang, dan pembaca kartu.

## 🚀 Fitur Utama

- **Live Camera View**: Tampilan kamera real-time dengan WebSocket
- **Card Reader Interface**: Interface pembaca kartu akses dengan validasi
- **Log Viewer**: Pencatatan dan filter aktivitas kendaraan
- **Gate Control**: Kontrol manual/otomatis gerbang parkir
- **System Statistics**: Dashboard statistik dan monitoring
- **Responsive Design**: UI modern dengan Tailwind CSS
- **Real-time Updates**: WebSocket untuk update langsung

## 🛠️ Teknologi

- **React 18** - Frontend framework
- **Vite** - Build tool dan dev server
- **Tailwind CSS** - Styling framework
- **Lucide React** - Icon library
- **React Router DOM** - Routing
- **React Hot Toast** - Notifications
- **WebSocket** - Real-time communication

## 📦 Instalasi

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build untuk production
npm run build

# Preview production build
npm run preview
```

## 🏗️ Struktur Project

```
src/
├── components/           # Komponen React
│   ├── LiveView.jsx     # Live camera component
│   ├── LogViewer.jsx    # Log viewer dengan filter
│   ├── CardReader.jsx   # Card reader interface
│   ├── GateControl.jsx  # Gate control panel
│   ├── SystemStats.jsx  # Dashboard statistics
│   ├── Sidebar.jsx      # Navigation sidebar
│   └── ui/              # UI components
├── pages/               # Halaman aplikasi
│   └── Dashboard.jsx    # Main dashboard
├── services/            # Services & API
│   └── websocket.js     # WebSocket service
├── lib/                 # Utilities
│   └── utils.js         # Helper functions
├── App.jsx              # Main app component
├── main.jsx             # Entry point
└── index.css            # Global styles
```

## 🔧 Komponen Utama

### LiveView
Menampilkan feed kamera secara real-time:
- WebSocket connection untuk streaming
- Fullscreen mode
- Camera controls dan settings
- Error handling dan reconnection

### CardReader
Interface untuk pembaca kartu akses:
- Real-time card detection
- Validasi kartu otomatis
- Riwayat pembacaan kartu
- Status connection indicator

### LogViewer
Viewer untuk log aktivitas sistem:
- Filter berdasarkan tipe aktivitas
- Search functionality
- Export ke CSV
- Auto-scroll dan manual scroll
- Real-time log updates

### GateControl
Panel kontrol gerbang parkir:
- Manual open/close gate
- Auto-close timer
- Arduino connection status
- Gate status indicators

### SystemStats
Dashboard statistik sistem:
- Total kendaraan masuk
- Okupansi parking
- Statistik harian
- Status sistem overall

## 🌐 WebSocket API

Frontend menggunakan WebSocket untuk komunikasi real-time dengan backend:

```javascript
// Koneksi WebSocket
ws://localhost:8000/ws

// Message types yang diterima:
- camera_frame: Frame kamera
- card_detected: Kartu terdeteksi
- gate_status: Status gerbang
- log_entry: Entry log baru
- system_status: Status sistem

// Message types yang dikirim:
- request_camera_stream: Request stream kamera
- gate_control: Kontrol gerbang
- card_read: Simulasi pembacaan kartu
```

## 🎨 Styling

Menggunakan Tailwind CSS dengan custom components:

```css
/* Custom classes tersedia: */
.card              # Card component
.btn               # Button variants
.status-online     # Status indicators
.animate-fade-in   # Custom animations
.scrollbar-thin    # Custom scrollbar
.glow-*           # Glow effects
```

## 🔄 State Management

Menggunakan React hooks untuk state management:
- `useState` untuk component state
- `useEffect` untuk side effects
- Custom hooks untuk WebSocket
- Context API untuk global state (jika diperlukan)

## 📱 Responsive Design

Interface responsive untuk berbagai ukuran layar:
- Desktop: Full layout dengan sidebar
- Tablet: Collapsed sidebar
- Mobile: Mobile-optimized layout

## 🔒 Error Handling

Error handling yang komprehensif:
- WebSocket reconnection otomatis
- Toast notifications untuk feedback
- Fallback UI untuk komponen error
- Graceful degradation

## ⚙️ Konfigurasi

Environment variables (optional):
```env
VITE_WEBSOCKET_URL=ws://localhost:8000/ws
VITE_API_URL=http://localhost:8000/api
```

## 🚦 Development

```bash
# Start dev server
npm run dev

# Check linting
npm run lint

# Format code
npm run format
```

## 📋 TODO / Roadmap

- [ ] Dark mode support
- [ ] PWA functionality
- [ ] Real camera integration
- [ ] Advanced filtering options
- [ ] User authentication
- [ ] Multi-language support
- [ ] Mobile app (React Native)

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - lihat file LICENSE untuk detail.

## 📞 Support

Untuk bantuan atau pertanyaan:

- Email: support@manlesspark.com
- GitHub Issues: [Create Issue](https://github.com/user/manless/issues)
- Documentation: [Wiki](https://github.com/user/manless/wiki)

---

**Manless Parking System** - Sistem Parkir Otomatis Modern 🚗💨
