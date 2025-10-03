"""GPS interface for GY-GPS6MV2 using /dev/serial0"""
import time
from datetime import datetime
from typing import Optional, Dict

try:
    import serial  # pyserial
    import pynmea2
except ImportError:
    serial = None
    pynmea2 = None
    print("Install dependencies: pip install pyserial pynmea2")

PORT = "/dev/serial0"
BAUD = 9600
_timeout = 1.0
_ser = None


def init_gps() -> bool:
    global _ser
    if serial is None:
        return False
    
    # Close any existing connection first
    if _ser is not None:
        try:
            _ser.close()
        except:
            pass
        _ser = None
    
    try:
        _ser = serial.Serial(PORT, BAUD, timeout=_timeout)
        # Clear any buffered data
        _ser.reset_input_buffer()
        return True
    except serial.SerialException as e:
        if "multiple access" in str(e).lower() or "device busy" in str(e).lower():
            print(f"GPS port busy - another process may be using it. Try: sudo fuser -k {PORT}")
        else:
            print(f"GPS init failed: {e}")
        return False
    except Exception as e:
        print(f"GPS init failed: {e}")
        return False


def _parse_gpgga(line: str) -> Optional[Dict]:
    if pynmea2 is None:
        return None
    try:
        msg = pynmea2.parse(line)
        if msg.sentence_type != 'GGA':
            return None
        # Fix quality 0 => invalid
        if getattr(msg, 'gps_qual', '0') in ('0', 0):
            return None
        # Convert lat/long to decimal degrees
        def _convert(value, direction):
            if not value:
                return None
            deg = int(float(value) / 100)
            minutes = float(value) - deg * 100
            dec = deg + minutes / 60.0
            if direction in ('S', 'W'):
                dec = -dec
            return dec
        lat = _convert(msg.lat, msg.lat_dir)
        lon = _convert(msg.lon, msg.lon_dir)
        alt = getattr(msg, 'altitude', None)
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'latitude': lat,
            'longitude': lon,
            'altitude': float(alt) if alt not in (None, '') else None
        }
    except Exception:
        return None


def read_data() -> Optional[Dict]:
    """Read latest valid GPS fix (GPGGA). Returns dict or None."""
    global _ser
    if _ser is None and not init_gps():
        return None
    try:
        start = time.time()
        while time.time() - start < 1.5:  # poll briefly
            if not _ser.is_open:
                if not init_gps():
                    return None
            line = _ser.readline().decode(errors='ignore').strip()
            if not line or 'GGA' not in line:
                continue
            data = _parse_gpgga(line)
            if data:
                return data
        return None
    except serial.SerialException as e:
        if "multiple access" in str(e).lower() or "device busy" in str(e).lower():
            # Port conflict - just return None silently and try again next time
            _ser = None
            return None
        else:
            print(f"GPS read error: {e}")
            return None
    except Exception as e:
        # Silent failure - GPS will retry on next call
        return None


def cleanup_gps():
    """Close GPS serial connection"""
    global _ser
    if _ser is not None:
        try:
            _ser.close()
        except:
            pass
        _ser = None
