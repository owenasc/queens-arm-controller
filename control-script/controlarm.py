import serial
import keyboard
import sys
import time
SERIAL_PORT = 'COM9'
BAUD_RATE = 9600

print("=" * 50)
print("HarveStar PC Keyboard Controller")
print("=" * 50)

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for connection to stabilize
    print(f"✓ Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
except Exception as e:
    print(f"✗ Error connecting to serial port: {e}")
    print("\nTroubleshooting:")
    print("  1. Check if the correct COM port is specified")
    print("  2. Make sure the Pico is plugged in")
    print("  3. Close any other programs using the serial port")
    sys.exit(1)

print("\nControls:")
print("  W/S - Move shoulder up/down")
print("  A/D - Move base left/right")
print("  Q/E - Move elbow up/down")
print("  Z/X - Open/close end effector")
print("  R - Reset to starting position")
print("  ESC - Exit")
print("\nPress and hold keys to control the robot...")
print("-" * 50)

keys_pressed = set()

def send_command(command):
    """Send a command to the Pico"""
    command = command + "\n"
    try:
        ser.write(command.encode())
        print(f"Sent: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")

try:
    # Main loop
    while True:
        # Check each control key
        if keyboard.is_pressed('w') and 'w' not in keys_pressed:
            keys_pressed.add('w')
        elif not keyboard.is_pressed('w') and 'w' in keys_pressed:
            keys_pressed.remove('w')
        
        if keyboard.is_pressed('s') and 's' not in keys_pressed:
            keys_pressed.add('s')
        elif not keyboard.is_pressed('s') and 's' in keys_pressed:
            keys_pressed.remove('s')
        
        if keyboard.is_pressed('a') and 'a' not in keys_pressed:
            keys_pressed.add('a')
        elif not keyboard.is_pressed('a') and 'a' in keys_pressed:
            keys_pressed.remove('a')
        
        if keyboard.is_pressed('d') and 'd' not in keys_pressed:
            keys_pressed.add('d')
        elif not keyboard.is_pressed('d') and 'd' in keys_pressed:
            keys_pressed.remove('d')
        
        if keyboard.is_pressed('q') and 'q' not in keys_pressed:
            keys_pressed.add('q')
        elif not keyboard.is_pressed('q') and 'q' in keys_pressed:
            keys_pressed.remove('q')
        
        if keyboard.is_pressed('e') and 'e' not in keys_pressed:
            keys_pressed.add('e')
        elif not keyboard.is_pressed('e') and 'e' in keys_pressed:
            keys_pressed.remove('e')
        
        if keyboard.is_pressed('up') and 'up' not in keys_pressed:
            keys_pressed.add('up')
        elif not keyboard.is_pressed('up') and 'up' in keys_pressed:
            keys_pressed.remove('up')
        
        if keyboard.is_pressed('down') and 'down' not in keys_pressed:
            keys_pressed.add('down')
        elif not keyboard.is_pressed('down') and 'down' in keys_pressed:
            keys_pressed.remove('down')
        
        if keyboard.is_pressed('space') and 'space' not in keys_pressed:
            keys_pressed.add('space')
        elif not keyboard.is_pressed('space') and 'space' in keys_pressed:
            keys_pressed.remove('space')
        
        # Exit on ESC
        if keyboard.is_pressed('esc'):
            print("\nExiting...")
            break

        command = ', '.join(str(key) for key in keys_pressed)

        if len(keys_pressed) > 0:
            send_command(command)
        time.sleep(0.1)  # Small delay to prevent CPU overload

except KeyboardInterrupt:
    print("\n\nKeyboard interrupt detected.")
except Exception as e:
    print(f"\nError: {e}")
finally:
    ser.close()
    print("Serial connection closed.")
    print("Goodbye!")