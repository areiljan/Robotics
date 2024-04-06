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

        self.left_wheel_speed = 27
        self.right_wheel_speed = 27

        self.right_base_speed = 0
        self.left_base_speed = 0

        self.wheel_circumference = self.robot.WHEEL_DIAMETER * math.pi
        self.machine_circumference = self.robot.AXIS_LENGTH * math.pi

        self.current_right_encoder = 0
        self.current_left_encoder = 0
        self.current_rotation = 0

        self.left_factor = 1
        self.right_factor = 1
        self.calibrated = False
        self.objects = []
        self.first_object_distance = 0
        self.second_object_distance = 0
        self.current_rotation_setpoint = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def calibrate(self):
        """Calibrate the robot."""
        self.left_wheel_speed = 9
        self.right_wheel_speed = 9

        if self.max_right_encoder > self.max_left_encoder:
            self.left_factor = round(1 + (1 - self.max_left_encoder / self.max_right_encoder), 2)
            self.left_wheel_speed = round(27 * self.left_factor / 3)
        elif self.max_right_encoder < self.max_left_encoder:
            self.right_factor = round(1 + (1 - self.max_right_encoder / self.max_left_encoder), 2)
            self.right_wheel_speed = round(27 * self.right_factor / 3)

        print("Corrections made", self.left_factor, self.right_factor)

    def find_objects(self):
        if self.objects < 2:
            self.move_right_on_place()
        else:
            self.state = "move_to_spot"
            self.current_rotation_setpoint = self.current_rotation

    def get_two_closest_objects_angle(self):
        """
        Find the closest visible object from the objects list.

        Returns:
          The angle (in radians) to the closest object w.r.t. the robot
          orientation (i.e., 0 is directly ahead) following the right
          hand rule (i.e., objects to the left have a plus sign and
          objects to the right have a minus sign).
          Must return None if no objects are visible.
        """
        degree_per_pixel = self.FOV[0] / self.resolution[0]
        closest_object = self.get_closest_object()
        camera_center_degrees = self.FOV[0] / 2

        if len(closest_object) > 0:
            object_x = closest_object[1][0]
            object_center_degrees = object_x * degree_per_pixel
            return math.radians(camera_center_degrees - object_center_degrees)
        return None

    def get_two_distances(self):
        """
        Give new values to the first_object_distance and the second_object_distance.

        (i.e., add new objects to the list as you detect them).
        """
        if (self.current_rotation - self.current_rotation_setpoint) < self.first_object_angle:
            # turn some way
            # give new value to self.first_object_distance
        if (self.current_rotation - self.current_rotation_setpoint) < self.second_object_angle:
            # turn some way
            # give new value to self.second_object_distance

    def hardcore_calculations(self):
        # calculate

    def get_front_middle_laser(self) -> Optional[float]:
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        self.sensor_data.append(self.middle_laser)
        if len(self.sensor_data) > 3:
            self.sensor_data.pop(0)
        median = statistics.median(self.sensor_data)
        return median if median != 0 else None

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

    def sense(self):
        """Sense method as per SPA architecture."""
        self.current_right_encoder = self.robot.get_right_wheel_encoder()
        self.current_left_encoder = self.robot.get_left_wheel_encoder()

        self.current_rotation = self.robot.get_rotation()
        self.objects = self.robot.get_camera_objects()
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
            self.left_wheel_speed = 27
            self.right_wheel_speed = 27
            if self.current_rotation < 360 * 3:
                self.move_left_on_place()
                self.max_left_encoder = abs(self.current_left_encoder)
                self.max_right_encoder = abs(self.current_right_encoder)
            else:
                self.calibrate()
                self.calibrated = True
                self.stop()
                self.state = "find_objects"
        elif self.state == "find_objects":
            self.find_objects()
        elif self.state == "find_object_distance":
            self.find_distance()
        elif self.state == "move_to_spot":


    def act(self):
        """Act according to plan."""
        print(self.robot.get_front_middle_laser(), self.get_front_middle_laser(), self.object_center_points)
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