# Built-in Python libraries, not visible in the CIRCUITPYTHON drive
import time
import board
import digitalio
import busio
import supervisor
import traceback
import usb_cdc
import math

# Python modules from the "lib" folder
from lib.harvestar import HarveStar

def seconds_since_boot():
    return f"{time.monotonic():.3f}"

# Initializing inputs and outputs
led_pin = digitalio.DigitalInOut(board.LED)
led_pin.direction = digitalio.Direction.OUTPUT
led_pin.value = True  # Turning on on-board LED
start_button = digitalio.DigitalInOut(board.GP14)
start_button.direction = digitalio.Direction.INPUT
start_button.pull = digitalio.Pull.UP
serial = usb_cdc.data

# Initialize the harvestar with proper piddns
print(seconds_since_boot() + " - Initializing HarveStar...")
harvestar = HarveStar(base_pin=board.GP0, shoulder_pin=board.GP1, elbow_pin=board.GP2, end_effector_pin=board.GP3)
# Wait for the button to be pressed
print(seconds_since_boot() + " - Press the button to start sequence.")

button_pressed_time = None

# Until the button is pressed, this loop will run
while True:
    # This part is for the long press
    if not start_button.value:
        if button_pressed_time is None:
            button_pressed_time = time.monotonic()
        elif time.monotonic() - button_pressed_time > 2:
            print(seconds_since_boot() + " - Button long pressed! Entering test mode...")
            led_pin.value = False
            # Enter test mode
            try:
                print("Harvestar Entering Controlled Mode")
                x, y, z = 18, 20, 5
                harvestar.move_multiple(x, y, z, 0.001)
                # Starting cylindrical coordinates
                r = math.sqrt(x**2 + y**2)   # horizontal distance
                phi = math.atan2(y, x)       # azimuth in radians
                z = z                         # vertical heighta
                ee = 90
                while (serial.in_waiting > 0):
                    serial.readline()
                while True:
                    new_r, new_phi, new_z, new_ee = r, phi, z, ee

                    if serial.in_waiting > 0:                # non-blocking — only reads if data is waiting
                        received_commands = serial.readline().decode().strip().split(",")
                        print(received_commands)
                        for command in received_commands:
                            command = command.lstrip()
                            if command == 'w':      # forward in radial direction
                                new_r += 0.5
                            elif command == 's':    # backward
                                new_r -= 0.5
                            elif command == 'a':    # rotate left
                                new_phi -= math.radians(2)  # small angular step (in radians)
                            elif command == 'd':    # rotate right
                                new_phi += math.radians(2)
                            elif command == 'up':  # move up
                                new_z += 0.5
                            elif command == 'down':  # move down
                                new_z -= 0.5
                            elif command == 'q':
                                new_ee -= 5
                            elif command == 'e':
                                new_ee += 5
                                
                        # Only move if anything changed
                        if new_r != r or new_phi != phi or new_z != z or new_ee != ee:
                            x = new_r * math.cos(new_phi)
                            y = new_r * math.sin(new_phi)
                            if harvestar.move_multiple(x, y, new_z, 0.001) == True:
                                r, phi, z = new_r, new_phi, new_z
                            else:
                                x = r * math.cos(phi)
                                y = r * math.sin(phi)
                                harvestar.move_multiple(x, y, z, 0.001)
                            if(new_ee <= 85 and new_ee >= 15):
                                harvestar.end_effector_move(new_ee)
                                ee = new_ee
                            
                            # Convert cylindrical to Cartesian for IK
                            x = r * math.cos(phi)
                            y = r * math.sin(phi)
                        time.sleep(0.05)
                    time.sleep(0.02)
            
            except Exception as e:
                print(seconds_since_boot() + " - ERROR: " + str(e))
                traceback.print_exception(e)
                print(seconds_since_boot() + " - Test mode aborted. Rebooting in 5 seconds...")
                time.sleep(5)
                supervisor.reload()

    # This part is for the short press
    else:
        if button_pressed_time is not None:
            if time.monotonic() - button_pressed_time <= 2:
                print(seconds_since_boot() + " - Button short pressed! Starting sequence...")
                led_pin.value = False
                break
        button_pressed_time = None

    time.sleep(0.05) # Short sleep as a good practice to lower the load and power consumption in a fast infinite loop


# Example sequence
print(seconds_since_boot() + " - Starting sequence...")
try:
    #get the raddish:
    harvestar.move_polar(25, 0, 15)   #move to a point
    harvestar.end_effector_move(80)   #open end effector
    harvestar.wait(2)                  #wait 1 second
    harvestar.move_polar(30, 0, 8)
    harvestar.wait(2)          #move down
    harvestar.end_effector_move(15) 
    harvestar.wait(2)         #close end effector
    harvestar.move_polar(30, 0, 25) 
    harvestar.wait(2)         #move up
    harvestar.move_polar(30, 120, 20)   #move to drop aaaaaaaaaaaaaaaaaaswaoff point
    harvestar.wait(2)                  #wait 1 second
    harvestar.end_effector_move(80)   #open end effector to drop off
    harvestar.wait(1)                  #wait 1 second

    




    """
    harvestar.move_multiple(25, 0, 15)
    harvestar.wait(2)
    harvestar.move_multiple(25, -5, 15)
    harvestar.wait(1)
    harvestar.move_multiple(25, 5, 15)
    harvestar.wait(1)
    harvestar.move_multiple(25, -5, 15)
    harvestar.wait(1)
    harvestar.move_multiple(25, 5, 15)
    harvestar.wait(1)"""

    


except Exception as e:
    print(seconds_since_boot() + " - ERROR: " + str(e))
    print(seconds_since_boot() + " - Sequence aborted. Rebooting in 5 seconds...")
    time.sleep(5)

print(seconds_since_boot() + " - Done. Automatic reboot...")
supervisor.reload()
