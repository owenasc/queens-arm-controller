import pwmio
from adafruit_motor import servo
import time
import sys
import math

def seconds_since_boot():
    return f"{time.monotonic():.3f}"

class ServoMotor:
    def __init__(self, pin, name, min_pulse=750, max_pulse=2250, actuation_range=180, start_angle=0):
        self.pwm = pwmio.PWMOut(pin, duty_cycle=2 ** 15, frequency=50)
        self.servo = servo.Servo(self.pwm, min_pulse=min_pulse, max_pulse=max_pulse, actuation_range=actuation_range)
        self.name = name
        self.start_angle = start_angle
        self.untested = True

class HarveStar:
    def __init__(self, base_pin, shoulder_pin, elbow_pin, end_effector_pin):
        # Initialize servos with names
        self.base = ServoMotor(base_pin, "Base", min_pulse=500, max_pulse=2500, actuation_range=180, start_angle=90)
        self.shoulder = ServoMotor(shoulder_pin, "Shoulder", min_pulse=500, max_pulse=1500, actuation_range=90, start_angle=0)
        self.elbow = ServoMotor(elbow_pin, "Elbow", min_pulse=500, max_pulse=1500, actuation_range=90, start_angle=60)
        self.end_effector = ServoMotor(end_effector_pin, "End_effector", min_pulse=850, max_pulse=2000, actuation_range=90, start_angle=90)

        # Initialize servo angles
        self.base.servo.angle = self.base.start_angle
        self.shoulder.servo.angle = self.shoulder.start_angle
        self.elbow.servo.angle = self.elbow.start_angle
        self.end_effector.servo.angle = self.end_effector.start_angle
        print(seconds_since_boot() + " - HarveStar initialized. Starting angles: Base: " + str(self.base.start_angle) + "°, Shoulder: " + str(self.shoulder.start_angle) + "°, Elbow: " + str(self.elbow.start_angle) + "°, End effector: " + str(self.end_effector.start_angle) + "°")


    def check_constraints(self, shoulder_angle, elbow_angle):
        constraints = [
            (0, 5, 55, 90),
            (5, 10, 40, 90),
            (10, 15, 40, 90),
            (15, 20, 35, 90),
            (20, 25, 25, 90),
            (25, 30, 20, 90),
            (30, 35, 15, 90),
            (35, 40, 10, 90),
            (40, 45, 5, 90),
            (45, 50, 5, 90),
            (50, 55, 0, 90),
            (55, 60, 0, 90),
            (60, 65, 0, 80),
            (65, 70, 0, 80),
            (70, 75, 0, 70),
            (75, 80, 0, 65),
            (80, 85, 0, 60),
            (85, 90, 0, 60)
        ]

        for s_low, s_high, e_low, e_high in constraints:
            if s_low <= shoulder_angle < s_high and not (e_low <= elbow_angle <= e_high):
                raise Exception(f"Constraint violated: When shoulder is between {s_low} and {s_high} degrees, elbow must be between {e_low} and {e_high} degrees.\r\nCurrent angles are: Shoulder: {math.ceil(shoulder_angle)}°, Elbow: {math.ceil(elbow_angle)}°")

    @staticmethod
    def compute_inverse_kinematics(x, y, z, L1 = 10, L2 = 13.225, L3 = 14.7):
        """Computes the joint angles θ1, θ2, θ3 given (x, y, z) position."""

        r = math.sqrt(x**2 + y**2)  # Horizontal distance
        d = math.sqrt(r**2 + (z - L1)**2)  # Distance from shoulder to target
        
        if d > (L2 + L3):
            raise ValueError("ERROR: Target position is out of reach!")

        theta1 = math.atan2(y, x) * (180 / math.pi)  # No need for absolute value
        theta3 = math.acos((L2**2 + L3**2 - d**2) / (2 * L2 * L3)) * (180 / math.pi)
        alpha = math.atan2(z - L1, r) * (180 / math.pi)  # No need for absolute value
        beta = math.acos((L2**2 + d**2 - L3**2) / (2 * L2 * d)) * (180 / math.pi)
        
        theta2 = alpha + beta 
        print("Moving to positoins: ", x, y, z) 
        print("Using angles: ", theta1, theta2, theta3)

        return theta1, theta2, theta3
    
    @staticmethod
    def compute_forward_kinematics(theta1, theta2, theta3, alpha, L1=10, L2=13.225, L3=14.7):
        """
        Computes the (x, y, z) position given joint angles θ1, θ2, θ3.
        Angles are assumed in degrees; this function internally converts to radians.
        """
        import math
        
        # Convert degrees to radians
        t1 = math.radians(theta1)
        t2 = math.radians(theta2)
        t3 = math.radians(theta3)

        # Planar XY distances before base rotation (theta1)
        # x' and z' come from the 2D forward kinematics in the plane
        x_prime = L2 * math.cos(t2) + L3 * math.cos(180-(theta2-alpha)-theta3-alpha) #Matts custum attempt (fail)
        z_prime = L2 * math.sin(t2) + L3 * math.sin(t2 + t3) #Chat GPT o1 attempt (fail)

        # Incorporate the rotation about z-axis (theta1) and base offset L1
        x = x_prime * math.cos(t1)
        y = x_prime * math.sin(t1)
        z = L1 + z_prime
        
        print(f"Forward kinematics calculated from (θ1, θ2, θ3)=({theta1}, {theta2}, {theta3}): ({x:.3f}, {y:.3f}, {z:.3f})")
        return x, y, z




    def move_multiple(self, x, y, z, end_effector_angle=None):
        #CHANGE MOVE MULTIPLE ARGUMENTS TO BE X, Y, Z THEN CALL INVERSE KINEMATICS FUNCTION

        # Start of new stuff
        print(f"Old y: {y}, Old x: {x}")

        base_angle = math.atan2(y, x) * (180 / math.pi)  # No need for absolute value

        print(f"Base angle for trig: {base_angle}")


        y -= 10.9 * math.sin(math.radians(base_angle))
        x -= 10.9 * math.cos(math.radians(base_angle))
        z += 1.8

        print(f"New y: {y}, New x: {x}")
        # END OF NEW STUFF

        base_angle, shoulder_angle, elbow_angle = HarveStar.compute_inverse_kinematics(x, y, z)

        base_angle = (base_angle* 1.50) + 90
        # base_angle = (base_angle* 1.5) - 45
        
        shoulder_angle = 110 - shoulder_angle
        elbow_angle -= shoulder_angle  # GOONER AH LINE THIS SHIT TOOK 1 HOUR

        # Verify constraints before moving
        self.check_constraints(shoulder_angle, elbow_angle)

        # Constraints are satisfied, move the HarveStar
        print(seconds_since_boot() + " - Moving HarveStar... Base: " + str(base_angle) + "°, Shoulder: " + str(shoulder_angle) + "°, Elbow: " + str(elbow_angle) + "°")
        self.base.servo.angle = base_angle
        self.shoulder.servo.angle = shoulder_angle
        self.elbow.servo.angle = elbow_angle
        if end_effector_angle is not None:
            self.end_effector.servo.angle = end_effector_angle
            print(seconds_since_boot() + " - End effector: " + str(end_effector_angle) + "°")

    def wait(self, seconds):
        print(seconds_since_boot() + " - Waiting for " + str(seconds) + " seconds...")
        time.sleep(seconds)

    def end_effector_open(self):
        print(seconds_since_boot() + " - Opening end effector...")
        self.end_effector.servo.angle = 90

    def end_effector_close(self):
        print(seconds_since_boot() + " - Closing end effector...")
        self.end_effector.servo.angle = 0