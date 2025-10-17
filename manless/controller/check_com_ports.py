#!/usr/bin/env python3
"""
Script untuk mengecek port COM yang tersedia di sistem
"""

try:
    import serial.tools.list_ports
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def check_com_ports():
        """Check available COM ports"""
        logger.info("🔍 Checking available COM ports...")
        
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            logger.warning("❌ No COM ports found!")
            return []
        
        logger.info(f"✅ Found {len(ports)} COM port(s):")
        
        for port in ports:
            logger.info(f"  📡 {port.device}: {port.description}")
            logger.info(f"     Hardware ID: {port.hwid}")
            logger.info(f"     Manufacturer: {port.manufacturer}")
            logger.info(f"     Product: {port.product}")
            logger.info("")
        
        return ports
    
    def test_arduino_connection(port_name: str, baudrate: int = 9600):
        """Test connection to Arduino on specific port"""
        logger.info(f"🔌 Testing Arduino connection on {port_name}...")
        
        try:
            import serial
            ser = serial.Serial(port_name, baudrate, timeout=2)
            
            if ser.is_open:
                logger.info(f"✅ Successfully opened {port_name}")
                
                # Send test command
                ser.write(b"STATUS\n")
                response = ser.readline().decode('utf-8').strip()
                
                if response:
                    logger.info(f"✅ Arduino responded: {response}")
                    ser.close()
                    return True
                else:
                    logger.warning(f"⚠️ No response from Arduino on {port_name}")
                    ser.close()
                    return False
            else:
                logger.error(f"❌ Failed to open {port_name}")
                return False
            
        except serial.SerialException as e:
            logger.error(f"❌ Serial error on {port_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error testing {port_name}: {e}")
            return False
    
    def suggest_arduino_port():
        """Suggest which port might be Arduino"""
        ports = check_com_ports()
        
        arduino_ports = []
        
        for port in ports:
            description = port.description.lower()
            manufacturer = (port.manufacturer or "").lower()
            product = (port.product or "").lower()
            
            # Check for Arduino indicators
            if any(keyword in description for keyword in ['arduino', 'uno', 'nano', 'mega']):
                arduino_ports.append(port.device)
            elif any(keyword in manufacturer for keyword in ['arduino', 'ftdi', 'ch340']):
                arduino_ports.append(port.device)
            elif any(keyword in product for keyword in ['arduino', 'uno', 'nano']):
                arduino_ports.append(port.device)
        
        if arduino_ports:
            logger.info(f"🎯 Suggested Arduino ports: {arduino_ports}")
            return arduino_ports
        else:
            logger.warning("⚠️ No obvious Arduino ports found")
            return []
    
    if __name__ == "__main__":
        print("=" * 50)
        print("COM PORT CHECKER - Arduino Detection")
        print("=" * 50)
        
        # Check all ports
        ports = check_com_ports()
        
        # Suggest Arduino ports
        arduino_ports = suggest_arduino_port()
        
        # Test suggested ports
        if arduino_ports:
            print("\n" + "=" * 50)
            print("TESTING ARDUINO CONNECTIONS")
            print("=" * 50)
            
            for port in arduino_ports:
                test_arduino_connection(port)
        
        print("\n" + "=" * 50)
        print("RECOMMENDATIONS")
        print("=" * 50)
        
        if arduino_ports:
            print(f"✅ Use one of these ports for Arduino: {arduino_ports}")
            print("📝 Update config_gate_in.py with the correct port")
        else:
            print("❌ No Arduino detected")
            print("🔧 Check Arduino connection and drivers")
        
        print("\n📋 Available ports for configuration:")
        for port in ports:
            print(f"   - {port.device}: {port.description}")

except ImportError:
    print("❌ pyserial not installed. Install with: pip install pyserial")
except Exception as e:
    print(f"❌ Error: {e}") 