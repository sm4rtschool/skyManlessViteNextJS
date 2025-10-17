#!/usr/bin/env python3
"""
Hardware Detector untuk Arduino dan Card Reader
Mendeteksi status koneksi hardware secara real-time
"""

import serial
import serial.tools.list_ports
import time
import logging
import threading
from typing import Dict, Optional, Callable, Tuple
import asyncio

# Konfigurasi
ARDUINO_DESCRIPTORS = ['arduino', 'uno', 'ch340', 'usb-serial']
PING_COMMAND = b"SKY_PARKING_AJIB\n"
EXPECTED_PONG_RESPONSE = "SKY_PARKING_AJIB"
STATUS_COMMAND = b"STATUS\n"
CONNECTION_TEST_TIMEOUT = 2.0  # Waktu tunggu untuk membaca balasan
POST_CONNECTION_DELAY = 2.0    # Waktu tunggu setelah port dibuka agar Arduino siap
DETECTION_INTERVAL = 5.0       # Diubah sesuai permintaan pengguna (5 detik)

class HardwareDetector:
    """Mendeteksi koneksi hardware seperti Arduino secara real-time di thread terpisah."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._status_callback: Optional[Callable] = None
        self._detection_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Kunci untuk memastikan thread-safe access ke status
        self._status_lock = threading.Lock()
        
        self._hardware_status = {
            "arduino": {"connected": False, "port": None, "gate_status": None, "last_check": None},
            "card_reader": {"connected": False, "port": None, "last_check": None}
        }
        self._previous_status = self._hardware_status.copy()

    def set_status_callback(self, callback: Callable):
        """Menetapkan fungsi callback yang akan dipanggil saat status berubah."""
        self.status_callback = callback

    def _is_potential_arduino_port(self, port) -> bool:
        """Memeriksa apakah port kemungkinan adalah Arduino berdasarkan deskripsinya."""
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        
        # Selalu anggap COM8 sebagai kandidat kuat jika ada
        if port.device == "COM8":
            return True
            
        return any(desc in description or desc in manufacturer for desc in ARDUINO_DESCRIPTORS)

    def _test_and_get_arduino_status(self, port: str, baudrate: int = 9600) -> Tuple[bool, Optional[str]]:
        """
        Menguji koneksi dengan PING, dan jika berhasil, mengambil status gerbang.
        Dibuat lebih kuat untuk menangani timing issue.
        """
        ser = None
        try:
            # Inisialisasi koneksi secara manual untuk mengatur DTR
            ser = serial.Serial()
            ser.port = port
            ser.baudrate = baudrate
            ser.timeout = CONNECTION_TEST_TIMEOUT
            ser.dtr = False # Mencegah auto-reset pada Arduino
            ser.open()

            time.sleep(POST_CONNECTION_DELAY)
            
            # Kosongkan semua data lama/startup di buffer
            ser.reset_input_buffer()
            if ser.in_waiting > 0:
                ser.read(ser.in_waiting)
            self.logger.debug(f"Buffer cleared on {port}")

            # 1. Uji koneksi dengan PING
            self.logger.debug(f"Sending PING to {port}...")
            ser.write(PING_COMMAND)
            ser.flush()
            
            time.sleep(0.5)
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            
            if response != EXPECTED_PONG_RESPONSE:
                self.logger.warning(f"No PONG from {port} (got: '{response}').")
                return False, None
            
            self.logger.debug(f"PONG received from {port}. Getting status...")

            # 2. Jika PONG berhasil, dapatkan status gerbang
            ser.write(STATUS_COMMAND)
            ser.flush()
            time.sleep(0.5)
            status_response = ser.readline().decode('utf-8', errors='ignore').strip()
            if status_response.startswith("GATE:"):
                gate_status = status_response.split(":")[1].lower()
                self.logger.info(f"✅ Arduino on {port} is responsive. Gate status: {gate_status}")
                return True, gate_status
            else:
                self.logger.warning(f"Unexpected STATUS response from {port}: '{status_response}'")
                return True, None

        except serial.SerialException as e:
            if "Access is denied" in str(e):
                self.logger.debug(f"Port {port} is busy, likely in use by another process.")
            else:
                self.logger.error(f"Serial error on {port}: {e}")
            return False, None
        except Exception as e:
            self.logger.error(f"Unexpected error testing {port}: {e}")
            return False, None
        finally:
            if ser and ser.is_open:
                ser.close()

    def _update_hardware_status(self):
        """Loop utama yang berjalan di thread untuk mendeteksi hardware."""
        while not self._stop_event.is_set():
            detected_ports = serial.tools.list_ports.comports()
            potential_arduino_ports = [p.device for p in detected_ports if self._is_potential_arduino_port(p)]
            
            arduino_found = False
            active_arduino_port = None
            gate_status = None

            if potential_arduino_ports:
                for port in potential_arduino_ports:
                    is_connected, current_gate_status = self._test_and_get_arduino_status(port)
                    if is_connected:
                        arduino_found = True
                        active_arduino_port = port
                        gate_status = current_gate_status
                        break 
            
            with self._status_lock:
                current_time = time.time()
                self._hardware_status["arduino"].update({
                    "connected": arduino_found,
                    "port": active_arduino_port,
                    "gate_status": gate_status, # Simpan status gerbang
                    "last_check": current_time
                })
                self._hardware_status["card_reader"].update({
                    "connected": False,
                    "port": None,
                    "last_check": current_time
                })

                status_changed = (self._hardware_status["arduino"] != self._previous_status["arduino"])
                if status_changed:
                    self.logger.info(f"Hardware status changed: {self._hardware_status['arduino']}")
                    self._previous_status = self._hardware_status.copy()
                    if self.status_callback:
                        try:
                            self.status_callback(self.get_status())
                        except Exception as e:
                            self.logger.error(f"Error executing status callback: {e}")
            
            time.sleep(DETECTION_INTERVAL)

    def start_detection(self):
        """Memulai thread deteksi hardware."""
        if self._detection_thread and self._detection_thread.is_alive():
            self.logger.warning("Detection thread already running.")
            return

        self.logger.info("Starting hardware detection thread...")
        self._stop_event.clear()
        self._detection_thread = threading.Thread(target=self._update_hardware_status, daemon=True)
        self._detection_thread.start()

    def stop_detection(self):
        """Menghentikan thread deteksi hardware."""
        self.logger.info("Stopping hardware detection thread...")
        self._stop_event.set()
        if self._detection_thread:
            self._detection_thread.join(timeout=5.0)
            if self._detection_thread.is_alive():
                self.logger.error("Detection thread failed to stop gracefully.")
        self.logger.info("Hardware detection stopped.")

    def get_status(self) -> Dict:
        """Mengembalikan status hardware terakhir yang diketahui (thread-safe)."""
        with self._status_lock:
            return self._hardware_status.copy()

# Singleton instance
hardware_detector = HardwareDetector()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    detector = HardwareDetector()

    def print_status_change(status):
        logger.info(f"CALLBACK: Status changed! New status: {status}")

    detector.set_status_callback(print_status_change)
    detector.start_detection()

    try:
        while True:
            time.sleep(10)
            current_status = detector.get_status()
            logger.info(f"MAIN THREAD: Polling status: {current_status}")

    except KeyboardInterrupt:
        logger.info("Shutdown requested.")
    finally:
        detector.stop_detection()
        logger.info("System shutdown.") 