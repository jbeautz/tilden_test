#!/usr/bin/env python3
"""
Touch input handler for pygame dummy driver
Reads touch events directly from /dev/input/event* and injects them as pygame events
"""

import threading
import struct
import time
import pygame
import os
import glob
import select

class TouchHandler:
    """Handles touch input by reading directly from input devices"""
    
    def __init__(self, on_touch_callback=None):
        self.running = False
        self.threads = []
        self.touch_devices = []
        self.last_touch_time = 0
        self.touch_debounce = 0.3  # 300ms debounce
        self.on_touch_callback = on_touch_callback
        
        # Track current touch position
        self.current_x = 0
        self.current_y = 0
        
        # Find all possible touch devices
        self._find_touch_devices()
    
    def _find_touch_devices(self):
        """Find all accessible input devices"""
        # Try all event devices
        for i in range(10):
            device = f'/dev/input/event{i}'
            if os.path.exists(device):
                try:
                    # Test if we can open it in non-blocking mode
                    fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
                    os.close(fd)
                    self.touch_devices.append(device)
                    print(f"Touch handler: Found accessible device: {device}")
                except:
                    pass
        
        if not self.touch_devices:
            print("Touch handler: No accessible input devices found")
            self.touch_devices = ['/dev/input/event0']  # Try anyway
    
    def start(self):
        """Start touch input threads for all devices"""
        if self.threads:
            return
        
        self.running = True
        # Start a thread for each device
        for device in self.touch_devices:
            thread = threading.Thread(target=self._read_touch_events, args=(device,), daemon=True)
            thread.start()
            self.threads.append(thread)
        print(f"Touch handler: Started monitoring {len(self.touch_devices)} device(s)")
        print("Touch handler: Touch the screen now - watching for events...")
    
    def stop(self):
        """Stop all touch input threads"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=1.0)
        self.threads = []
        print("Touch handler: Stopped")
    
    def _read_touch_events(self, device_path):
        """Read touch events from input device and inject pygame events"""
        try:
            # Open device in non-blocking mode
            fd = os.open(device_path, os.O_RDONLY | os.O_NONBLOCK)
            print(f"Touch handler: Monitoring {device_path}")
            
            # Event format: (time_sec, time_usec, type, code, value)
            event_size = struct.calcsize('llHHi')
            start_time = time.time()
            
            while self.running:
                try:
                    # Use select to wait for data
                    readable, _, _ = select.select([fd], [], [], 0.1)
                    
                    if not readable:
                        continue
                    
                    data = os.read(fd, event_size)
                    if not data or len(data) < event_size:
                        continue
                    
                    tv_sec, tv_usec, ev_type, code, value = struct.unpack('llHHi', data)
                    
                    # Debug: Print all non-zero events for first 30 seconds
                    if time.time() - start_time < 30 and ev_type != 0:
                        print(f"Touch [{device_path}]: type={ev_type}, code={code}, value={value}")
                    
                    # EV_ABS (type 3) - Absolute position events (touchscreen)
                    if ev_type == 3:
                        if code == 53:  # ABS_MT_POSITION_X
                            self.current_x = value
                        elif code == 54:  # ABS_MT_POSITION_Y
                            self.current_y = value
                    
                    # EV_KEY (type 1) - Button/key events (BTN_TOUCH)
                    # Trigger on button press (value==1)
                    if ev_type == 1 and code == 330 and value == 1:  # BTN_TOUCH pressed
                        current_time = time.time()
                        if current_time - self.last_touch_time > self.touch_debounce:
                            self.last_touch_time = current_time
                            print(f"✅ TOUCH DETECTED on {device_path} at ({self.current_x}, {self.current_y})")
                            
                            # Call the callback with position
                            if self.on_touch_callback:
                                self.on_touch_callback(self.current_x, self.current_y)
                            
                            # Also inject mouse click into pygame at the touch position
                            try:
                                mouse_event = pygame.event.Event(
                                    pygame.MOUSEBUTTONDOWN,
                                    {'pos': (self.current_x, self.current_y), 'button': 1}
                                )
                                pygame.event.post(mouse_event)
                            except:
                                pass  # Ignore if pygame event queue is full
                    
                except (IOError, OSError) as e:
                    # Device might be temporarily unavailable
                    if e.errno != 11:  # Ignore EAGAIN (no data available)
                        time.sleep(0.1)
                    continue
            
            os.close(fd)
                    
        except Exception as e:
            print(f"Touch handler error on {device_path}: {e}")
    
    def __del__(self):
        self.stop()


# Global instance
_touch_handler = None

def init(on_touch_callback=None):
    """Initialize touch handler with optional callback"""
    global _touch_handler
    if _touch_handler is None:
        _touch_handler = TouchHandler(on_touch_callback=on_touch_callback)
        _touch_handler.start()

def cleanup():
    """Clean up touch handler"""
    global _touch_handler
    if _touch_handler:
        _touch_handler.stop()
        _touch_handler = None
