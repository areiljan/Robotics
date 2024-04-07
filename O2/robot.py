"""O2 - Objects."""
import math
import statistics
from typing import Optional
import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        # ROBOT
        self.robot = PiBot.PiBot()
        self.shutdown = False

        # STATE
        self.state = "find_objects"
        self.add = True

        # LEFT WHEEL
        self.left_wheel_speed = 8
        self.left_base_speed = 0
        self.left_factor = 1

        # RIGHT WHEEL
        self.right_wheel_speed = 8
        self.right_base_speed = 0
        self.right_factor = 1

        # CONSTANTS
        self.wheel_circumference = self.robot.WHEEL_DIAMETER * math.pi
        self.machine_circumference = self.robot.AXIS_LENGTH * math.pi

        # LEFT ENCODER
        self.current_left_encoder = 0
        self.max_left_encoder = 0

        # RIGHT ENCODER
        self.current_right_encoder = 0
        self.max_right_encoder = 0

        # ROTATION
        self.current_rotation = 0
        self.rotation_before_finding = 0

        # LASER
        self.sensor_data = []
        self.middle_laser = 0

        # OBJECT FINDING
        self.object_start = 0
        self.object_end = 0
        self.object_center_points = []

        # OBJECT DISTANCE
        self.distance = 0
        self.furthest = 0
        self.first_object_distance = 0
        self.second_object_distance = 0

        # SPOT LOCATION
        self.robots_spot_degrees = None
        self.robots_spot_distance = None

        # CALCULATIONS
        self.x = 0
        self.x_to_move = 0
        self.y_to_move = 0

        # ODOMETRICS
        self.right_encoder = 0
        self.last_right_encoder = 0
        self.delta_right_encoder = 0

        self.left_encoder = 0
        self.last_left_encoder = 0
        self.delta_left_encoder = 0

        self.encoder_x = 0
        self.encoder_y = 0
        self.encoder_yaw = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

# ------------------------------------------------------------
# |                    PROBLEM SOLUTION                      |
# ------------------------------------------------------------

    def get_front_middle_laser(self) -> Optional[float]:
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        return self.middle_laser

    def add_objects(self):
        """
        Return the list with the detected objects so far.

        (i.e., add new objects to the list as you detect them).

        Returns:
          The list with detected object angles, the angles are in
          degrees [0..360), 0 degrees being the start angle and following
          the right-hand rule (e.g., turning left 90 degrees is 90, turning
          right 90 degrees is 270 degrees).
        """
        middle_laser = self.get_front_middle_laser()
        if middle_laser is not None and middle_laser < 0.7:
            if self.object_start == 0:
                self.object_start = self.current_rotation
            if middle_laser > self.distance:
                self.distance = middle_laser
            self.object_end = self.current_rotation
        else:
            if self.object_start != 0:
                object_degrees = self.object_end - self.object_start
                if object_degrees < 30:
                    object_middle_point = self.object_end - (object_degrees / 2)
                    self.object_center_points.append(object_middle_point)
                    if self.first_object_distance == 0:
                        self.first_object_distance = self.distance
                    elif self.first_object_distance != 0 and self.second_object_distance == 0:
                        self.second_object_distance = self.distance
                    print("added object at:", object_middle_point, "with distance:", self.first_object_distance if self.second_object_distance == 0 else self.second_object_distance )

                self.object_start = 0
                self.object_end = 0
                self.distance = 0
        if 0.16 < self.first_object_distance > 0.24 or self.first_object_distance < 0.16:
            self.add = False

    def find_objects(self):
        """Find objects around robot."""
        if self.current_rotation < self.rotation_before_finding + 360:
            self.move_left_on_place()
            self.add_objects()
            if len(self.object_center_points) == 2:
                self.stop()
                if self.first_object_distance > self.second_object_distance:
                    self.furthest = self.object_center_points[0]
                else:
                    self.furthest = self.object_center_points[1]
                self.state = "turn_to_furthest_object"
                print("objects found:", self.object_center_points)

    def turn_to_furthest_object(self):
        """Turn to the furthest object."""
        if self.current_rotation > self.furthest:
            self.move_right_on_place()
        else:
            self.stop()
            print("looking at the furthest object")
            self.state = "hardcore_calculations"

    def hardcore_calculations(self):
        """Do calculations in order to find corrects spot for robot."""
        d1 = self.first_object_distance  # robot's distance from first object
        print("d1:", d1)
        d2 = self.second_object_distance  # robot's distance from second object
        print("d2:", d2)
        delta_a = abs(self.object_center_points[1] - self.object_center_points[0])  # degrees between objects
        if delta_a > 180:
            delta_a = 360 - delta_a
        print("delta alpha:", delta_a)
        r = math.sqrt(d1 ** 2 + d2 ** 2 - 2 * d1 * d2 * math.cos(math.radians(delta_a)))  # distance between objects
        print("r:", r)
        corner_b = math.degrees(math.acos((r ** 2 + d2 ** 2 - d1 ** 2) / (2 * r * d2)))  # corner between r and d2
        print("beta", corner_b)
        self.x = math.sqrt(r ** 2 + d2 ** 2 - 2 * r * d2 * math.cos(math.radians(60 - corner_b)))  # distance from robots correct spot
        print("x:", self.x)
        result = (d2 ** 2 + self.x ** 2 - r ** 2) / (2 * r * d2)
        result = min(1, max(-1, result))
        corner_l = math.degrees(math.acos(result))  # corner between d2 and x
        print("lambda:", corner_l)

        self.robots_spot_distance = self.x
        if self.add:
            self.robots_spot_degrees = self.current_rotation + corner_l
        else:
            self.robots_spot_degrees = self.current_rotation - corner_l

        print("current rotation:", self.current_rotation, "spot degrees:", self.robots_spot_degrees)
        self.state = "looking_towards_spot"

    def looking_towards_spot(self):
        """Guide robot to the correct spot in order to make equilateral triangle."""
        if self.current_rotation > self.robots_spot_degrees + 1:
            self.move_right_on_place()
        elif self.current_rotation < self.robots_spot_degrees - 1:
            self.move_left_on_place()
        else:
            self.stop()
            self.x_to_move = abs(self.x * math.sin(self.current_rotation))
            self.y_to_move = abs(self.x * math.cos(self.current_rotation))
            print("Locations to move: x: " + str(self.x_to_move) + " y: " + str(self.y_to_move))
            print("Looking towards spot")
            self.state = "move_to_spot"

    def move_towards_spot(self):
        """Guide robot to the correct spot in order to make equilateral triangle."""
        if abs(self.encoder_x) < self.y_to_move and abs(self.encoder_y) < self.x_to_move:
            self.move_forward()

        else:
            self.stop()
            self.state = "finito"
        # Move self.robots_spot_distance amount forward... BUT HOW? encoders are the answer :( --- they suck
        print("x: " + str(self.encoder_x) + " y:" + str(self.encoder_y) + " yaw: " + str(self.encoder_yaw))


    def calculate_encoder_odometry(self):
        """Calculate the encoder odometry values."""
        self.encoder_yaw += (self.robot.WHEEL_DIAMETER / 2 / self.robot.AXIS_LENGTH) * (self.delta_right_encoder - self.delta_left_encoder)
        self.encoder_x += (self.robot.WHEEL_DIAMETER / 4) * (self.delta_left_encoder + self.delta_right_encoder) * math.cos(self.encoder_yaw)
        self.encoder_y += (self.robot.WHEEL_DIAMETER / 4) * (self.delta_left_encoder + self.delta_right_encoder) * math.sin(self.encoder_yaw)

    def get_encoder_odometry(self):
        """
        Return the encoder odometry.

        Returns:
           A tuple with x, y coordinates and yaw angle (x, y, yaw)
           based on encoder data. The units must be (meters, meters, radians).
        """
        return self.encoder_x, self.encoder_y, self.current_rotation

# ------------------------------------------------------------
# |                      MOVEMENT                            |
# ------------------------------------------------------------

    def move_forward(self):
        """Set robot movement to forward."""
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = self.right_wheel_speed

    def move_backward(self):
        """Set robot movement to backward."""
        self.left_base_speed = -self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed

    def move_right(self):
        """Set robot movement to right."""
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed + 2 * self.right_factor

    def move_left(self):
        """Set robot movement to left."""
        self.left_base_speed = -self.left_wheel_speed + 2 * self.left_factor
        self.right_base_speed = self.right_wheel_speed

    def move_right_on_place(self):
        """Set robot movement to right."""
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed

    def move_left_on_place(self):
        """Set robot movement to left."""
        self.left_base_speed = -self.left_wheel_speed
        self.right_base_speed = self.right_wheel_speed

    def stop(self):
        """Set robot movement to halt."""
        self.left_base_speed = 0
        self.right_base_speed = 0

# ------------------------------------------------------------
# |                          SPA                             |
# ------------------------------------------------------------
    def sense(self):
        """Sense method as per SPA architecture."""
        self.left_encoder = math.radians(self.robot.get_left_wheel_encoder())
        self.right_encoder = math.radians(self.robot.get_right_wheel_encoder())

        self.middle_laser = self.robot.get_front_middle_laser()

        self.delta_left_encoder = self.left_encoder - self.last_left_encoder
        self.delta_right_encoder = self.right_encoder - self.last_right_encoder
        self.current_rotation = self.robot.get_rotation()

        self.calculate_encoder_odometry()

        self.last_left_encoder = self.left_encoder
        self.last_right_encoder = self.right_encoder


    def plan(self):
        """
        Return the direction of the line based on sensor readings.

        Returns:
          -1: Line is on the right (i.e., the robot should turn right to reach the line again)
           0: Robot is on the line (i.e., the robot should not turn to stay on the line) or no sensor info
           1: Line is on the left (i.e., the robot should turn left to reach the line again)
        """
        if self.state == "find_objects":
            self.find_objects()
            print(str(self.get_front_middle_laser()))
        elif self.state == "turn_to_furthest_object":
            self.turn_to_furthest_object()
        elif self.state == "hardcore_calculations":
            self.hardcore_calculations()
        elif self.state == "looking_towards_spot":
            self.looking_towards_spot()
        elif self.state == "move_to_spot":
            self.move_towards_spot()
        elif self.state == "finito":
            pass
    def act(self):
        """Act according to plan."""
        self.robot.set_left_wheel_speed(self.left_base_speed)
        self.robot.set_right_wheel_speed(self.right_base_speed)

    def spin(self):
        """Start the main loop of the robot."""
        while not self.shutdown:
            self.sense()
            self.plan()
            self.act()
            self.robot.sleep(0.05)


# ------------------------------------------------------------
# |                          MAIN                            |
# ------------------------------------------------------------


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
