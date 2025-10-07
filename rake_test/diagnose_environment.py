#!/usr/bin/env python3
"""
Diagnostic script to check the environment when run by systemd vs manual.
This will help us understand why it works manually but fails on boot.
"""
import os
import sys
import subprocess
from datetime import datetime

print("=" * 70)
print("ENVIRONMENT DIAGNOSTIC")
print("=" * 70)
print(f"Time: {datetime.now()}")
print()

# 1. User and permissions
print("USER & PERMISSIONS:")
print(f"  User: {os.getenv('USER', 'not set')}")
print(f"  Home: {os.getenv('HOME', 'not set')}")
print(f"  UID: {os.getuid()}")
print(f"  GID: {os.getgid()}")
print(f"  Groups: {os.getgroups()}")
print()

# 2. Working directory
print("WORKING DIRECTORY:")
print(f"  CWD: {os.getcwd()}")
print(f"  Script location: {os.path.abspath(__file__)}")
print()

# 3. Display/framebuffer access
print("DISPLAY/FRAMEBUFFER ACCESS:")
fb_devices = ['/dev/fb0', '/dev/fb1']
for fb in fb_devices:
    if os.path.exists(fb):
        try:
            stat = os.stat(fb)
            readable = os.access(fb, os.R_OK)
            writable = os.access(fb, os.W_OK)
            print(f"  {fb}: exists, readable={readable}, writable={writable}")
            print(f"    Permissions: {oct(stat.st_mode)[-3:]}")
            print(f"    Owner: uid={stat.st_uid}, gid={stat.st_gid}")
        except Exception as e:
            print(f"  {fb}: exists but error: {e}")
    else:
        print(f"  {fb}: NOT FOUND")
print()

# 4. SDL environment
print("SDL ENVIRONMENT:")
sdl_vars = ['SDL_VIDEODRIVER', 'SDL_FBDEV', 'SDL_NOMOUSE', 'DISPLAY']
for var in sdl_vars:
    val = os.getenv(var, 'not set')
    print(f"  {var}: {val}")
print()

# 5. DRM devices
print("DRM/GRAPHICS DEVICES:")
drm_devices = ['/dev/dri/card0', '/dev/dri/card1', '/dev/dri/renderD128']
for drm in drm_devices:
    if os.path.exists(drm):
        readable = os.access(drm, os.R_OK)
        writable = os.access(drm, os.W_OK)
        print(f"  {drm}: exists, readable={readable}, writable={writable}")
    else:
        print(f"  {drm}: NOT FOUND")
print()

# 6. Video group membership
print("VIDEO GROUP CHECK:")
try:
    result = subprocess.run(['groups'], capture_output=True, text=True)
    groups = result.stdout.strip()
    has_video = 'video' in groups
    print(f"  Current groups: {groups}")
    print(f"  Member of 'video' group: {has_video}")
except Exception as e:
    print(f"  Error checking groups: {e}")
print()

# 7. Try importing pygame
print("PYGAME TEST:")
try:
    import pygame
    print("  ✓ pygame imported successfully")
    print(f"    pygame version: {pygame.version.ver}")
    print(f"    SDL version: {pygame.version.SDL}")
    
    # Try to get available drivers
    try:
        pygame.init()
        drivers = pygame.display.get_driver()
        print(f"    Available driver: {drivers}")
    except Exception as e:
        print(f"    Could not check drivers: {e}")
except Exception as e:
    print(f"  ✗ pygame import failed: {e}")
print()

# 8. Boot timing check
print("BOOT TIMING:")
try:
    with open('/proc/uptime', 'r') as f:
        uptime = float(f.read().split()[0])
        print(f"  System uptime: {uptime:.1f} seconds")
        if uptime < 30:
            print(f"  ⚠ WARNING: System booted very recently (< 30s)")
            print(f"     Graphics subsystem may not be fully initialized")
except Exception as e:
    print(f"  Could not check uptime: {e}")
print()

print("=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
