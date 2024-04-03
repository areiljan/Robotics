"""EX06 - Object Detection."""
import PiBot
import statistics
import math


class Robot:
    """Robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

        self.wheel_circumference = self.robot.WHEEL_DIAMETER * math.pi
        self.machine_circumference = self.robot.AXIS_LENGTH * math.pi
        self.middle_laser = 0
        self.left_encoder = 0
        self.right_encoder = 0

        self.sensor_data = [0, 0, 0, 0, 0]
        self.object_start = 0
        self.object_end = 0

        self.object_list = []

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set Robot reference."""
        self.robot = robot

    def get_objects(self) -> list:
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
        if middle_laser is not None and 0.1 < middle_laser <= 0.45:
            if self.object_start == 0:
                self.object_start = self.right_encoder
            self.object_end = self.right_encoder
        else:
            if self.object_start != 0:
                difference = abs(self.object_end - self.object_start)
                meters_turned = difference / 360 * self.wheel_circumference
                rotation = meters_turned / self.machine_circumference * 360
                object_center_degrees = rotation / 2

                meters_turned_until_object = self.object_start / 360 * self.wheel_circumference
                rotation_until_object = meters_turned_until_object / self.machine_circumference * 360

                rotation_until_object_center = rotation_until_object + object_center_degrees if rotation_until_object > 0 else rotation_until_object - object_center_degrees
                result = rotation_until_object_center if rotation_until_object_center > 0 else 360 + rotation_until_object_center
                self.object_list.append(result)

                self.object_start = 0
                self.object_end = 0

        return self.object_list

    def get_front_middle_laser(self) -> None | float:
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

    def sense(self):
        """Sense method according to the SPA architecture."""
        self.middle_laser = self.robot.get_front_middle_laser()
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.right_encoder = self.robot.get_right_wheel_encoder()

    def spin(self):
        """Execute the spin loop."""
        while not self.shutdown:
            print(f'Value is {self.get_front_middle_laser()}')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.shutdown = True


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
