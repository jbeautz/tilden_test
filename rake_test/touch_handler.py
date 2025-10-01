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

class TouchHandler:
    """Handles touch input by reading directly from input devices"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.touch_device = None
        self.last_touch_time = 0
        self.touch_debounce = 0.3  # 300ms debounce
        
        # Find touch device
        self._find_touch_device()
    
    def _find_touch_device(self):
        """Find the touchscreen input device"""
        # Try common touch device paths
        possible_devices = [
            '/dev/input/event0',  # Most common for DSI displays
            '/dev/input/event1',
            '/dev/input/event2',
            '/dev/input/mouse0',
            '/dev/input/mice',
        ]
        
        for device in possible_devices:
            if os.path.exists(device):
                try:
                    # Test if we can open it
                    with open(device, 'rb') as f:
                        self.touch_device = device
                        print(f"Touch handler: Using {device} for touch input")
                        return
                except:
                    continue
        
        print("Touch handler: No accessible touch device found")
        # Default to event0 anyway
        self.touch_device = '/dev/input/event0'
    
    def start(self):
        """Start the touch input thread"""
        if self.thread and self.thread.is_alive():
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._read_touch_events, daemon=True)
        self.thread.start()
        print("Touch handler: Started")
    
    def stop(self):
        """Stop the touch input thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("Touch handler: Stopped")
    
    def _read_touch_events(self):
        """Read touch events from input device and inject pygame events"""
        if not self.touch_device:
            print("Touch handler: No device configured")
            return
        
        try:
            with open(self.touch_device, 'rb') as device:
                print(f"Touch handler: Monitoring {self.touch_device} - Touch screen now!")
                
                # Event format: (time_sec, time_usec, type, code, value)
                event_size = struct.calcsize('llHHi')
                
                while self.running:
                    try:
                        data = device.read(event_size)
                        if not data or len(data) < event_size:
                            time.sleep(0.01)
                            continue
                        
                        tv_sec, tv_usec, ev_type, code, value = struct.unpack('llHHi', data)
                        
                        # Debug: Print all events for first 10 seconds
                        if time.time() - self.last_touch_time < 10:
                            if ev_type != 0:  # Ignore sync events
                                print(f"Touch handler: Event type={ev_type}, code={code}, value={value}")
                        
                        # EV_KEY (type 1) - Button/key events
                        # EV_ABS (type 3) - Absolute position events (touchscreen)
                        # BTN_TOUCH (code 330), BTN_LEFT (code 272)
                        if (ev_type == 1 and value == 1):  # Any button press
                            current_time = time.time()
                            if current_time - self.last_touch_time > self.touch_debounce:
                                self.last_touch_time = current_time
                                print(f"Touch handler: Touch/Click detected! (code={code})")
                                
                                # Inject SPACE key press into pygame
                                key_event = pygame.event.Event(
                                    pygame.KEYDOWN,
                                    {'key': pygame.K_SPACE, 'mod': 0, 'unicode': ' '}
                                )
                                pygame.event.post(key_event)
                        
                    except (IOError, OSError) as e:
                        # Device might be temporarily unavailable
                        time.sleep(0.1)
                        continue
                        
        except Exception as e:
            print(f"Touch handler error: {e}")
    
    def __del__(self):
        self.stop()


# Global instance
_touch_handler = None

def init():
    """Initialize touch handler"""
    global _touch_handler
    if _touch_handler is None:
        _touch_handler = TouchHandler()
        _touch_handler.start()

def cleanup():
    """Clean up touch handler"""
    global _touch_handler
    if _touch_handler:
        _touch_handler.stop()
        _touch_handler = None
