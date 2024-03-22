"""EX04 - Objects."""
import math
import statistics
from typing import Optional

import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.state = "calibrate"

        self.left_wheel_speed = 10
        self.right_wheel_speed = 10

        self.right_base_speed = 0
        self.left_base_speed = 0

        self.wheel_circumference = self.robot.WHEEL_DIAMETER * math.pi
        self.machine_circumference = self.robot.AXIS_LENGTH * math.pi

        self.object_center_points = []
        self.object_start = 0
        self.object_end = 0

        self.current_right_encoder = 0
        self.current_left_encoder = 0
        self.current_rotation = 0

        self.max_right_encoder = 0
        self.max_left_encoder = 0

        self.left_factor = 1
        self.right_factor = 1
        self.calibrated = False

        self.sensor_data = []
        self.middle_laser = 0

        self.startpoint = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def calibrate(self):
        """Calibrate the robot."""
        self.left_wheel_speed = 10
        self.right_wheel_speed = 10

        if self.max_right_encoder > self.max_left_encoder:
            self.left_factor = round(1 + (1 - self.max_left_encoder / self.max_right_encoder), 2)
            self.left_wheel_speed = round(20 * self.left_factor / 2)
        elif self.max_right_encoder < self.max_left_encoder:
            self.right_factor = round(1 + (1 - self.max_right_encoder / self.max_left_encoder), 2)
            self.right_wheel_speed = round(20 * self.right_factor / 2)

        print("Corrections made", self.right_factor, self.left_factor)

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
        if middle_laser is not None and middle_laser == 2.0:
            if self.object_start == 0:
                self.object_start = self.current_rotation
            self.object_end = self.current_rotation
        else:
            if self.object_start != 0:
                object_middle_point = self.object_end - ((self.object_end - self.object_start) / 2)
                self.object_center_points.append(object_middle_point)

                self.object_start = 0
                self.object_end = 0

    def get_front_middle_laser(self) -> Optional[float]:
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        self.sensor_data.append(self.middle_laser)
        if len(self.sensor_data) > 5:
            self.sensor_data.pop(0)
        median = statistics.median(self.sensor_data)
        return median if median != 0 else None

    def move_forward(self):
        """Set robot movement to forward."""
        # self.state = "forward"
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = self.right_wheel_speed

    def move_backward(self):
        """Set robot movement to backward."""
        # self.state = "backward"
        self.left_base_speed = -self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed

    def move_right(self):
        """Set robot movement to right."""
        # self.state = "right"
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed + 2 * self.right_factor

    def move_left(self):
        """Set robot movement to left."""
        # self.state = "left"
        self.left_base_speed = -self.left_wheel_speed + 2 * self.left_factor
        self.right_base_speed = self.right_wheel_speed

    def move_right_on_place(self):
        """Set robot movement to right."""
        # self.state = "right"
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed

    def move_left_on_place(self):
        """Set robot movement to left."""
        # self.state = "left"
        self.left_base_speed = -self.left_wheel_speed
        self.right_base_speed = self.right_wheel_speed

    def stop(self):
        """Set robot movement to halt."""
        # self.state = "stop"
        self.left_base_speed = 0
        self.right_base_speed = 0

    def find_objects(self):
        """Find objects around robot."""
        # self.state = "find"
        if len(self.object_center_points) < 1:
            self.move_left_on_place()
            self.add_objects()
        else:
            self.state = "turn_to_object"

    def turn_to_object(self):
        """
        Turn to the object.
        """
        if self.current_rotation > self.object_center_points[0]:
            self.move_right_on_place()
        else:
            self.state = "move_to_object"

    def sense(self):
        """Sense method as per SPA architecture."""
        self.current_right_encoder = self.robot.get_right_wheel_encoder()
        self.current_left_encoder = self.robot.get_left_wheel_encoder()

        self.current_rotation = self.robot.get_rotation()
        self.middle_laser = self.robot.get_front_middle_laser()

    def plan(self):
        """
        Return the direction of the line based on sensor readings.

        Returns:
          -1: Line is on the right (i.e., the robot should turn right to reach the line again)
           0: Robot is on the line (i.e., the robot should not turn to stay on the line) or no sensor info
           1: Line is on the left (i.e., the robot should turn left to reach the line again)
        """
        if not self.calibrated:
            self.left_wheel_speed = 20
            self.right_wheel_speed = 20
            if self.current_rotation < 360 * 3:
                self.move_left_on_place()
                self.max_left_encoder = abs(self.current_left_encoder)
                self.max_right_encoder = abs(self.current_right_encoder)
            else:
                self.calibrate()
                self.calibrated = True
                self.state = "find_objects"
        elif self.state == "find_objects":
            self.find_objects()
        elif self.state == "turn_to_object":
            self.turn_to_object()
        elif self.state == "move_to_object":
            self.stop()

    def act(self):
        """Act according to plan."""
        print("middle laser: " + str(self.get_front_middle_laser()), "points: " + str(self.object_center_points))
        print("current rotation" + str(self.current_rotation))
        self.robot.set_left_wheel_speed(self.left_base_speed)
        self.robot.set_right_wheel_speed(self.right_base_speed)

    def spin(self):
        """Start the main loop of the robot."""
        while not self.shutdown:
            self.sense()
            self.plan()
            self.act()
            self.robot.sleep(0.05)


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
