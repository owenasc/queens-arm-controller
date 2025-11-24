# Built-in Python libraries, not visible in the CIRCUITPYTHON drive
import time
import board
import digitalio
import supervisor
import traceback

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

# Initialize the harvestar with proper pins
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
                harvestar.enter_controlled_mode()
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
    harvestar.move_multiple(16.5, 20.5, 3.5)
    harvestar.wait(0.5)
    harvestar.end_effector_move(20)
    harvestar.move_multiple(20, 24, 2.5)
    harvestar.wait(0.4)
    harvestar.end_effector_move(90)

    




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
