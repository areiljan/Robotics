"""EX15 - Mapping with sensors."""
import math

import PiBot


class Robot:
    """Robot class."""

    def __init__(self, initial_odom: list = [0, 0, 0],
                 cell_size: float = 0.3, heading_tolerance: float = 5):
        """
        Initialize variables.

        Arguments:
          initial_odom -- Initial odometry, [x, y, yaw] in
            [meters, meters, radians]
          cell_size -- cell edge length in meters
          heading_tolerance -- the number of degrees
            deviation (+/-) allowed for direction classification
        """
        self.cell_size = cell_size
        self.heading_tolerance = heading_tolerance

        self.robot = PiBot.PiBot()

        self.imu_x = initial_odom[0]
        self.imu_y = initial_odom[1]
        self.initial_yaw = initial_odom[2]

        self.rotation = None
        self.left_encoder = 0
        self.right_encoder = 0
        self.delta_left_encoder = 0
        self.delta_right_encoder = 0
        self.last_left_encoder = 0
        self.last_right_encoder = 0


    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set PiBot reference."""
        self.robot = robot


    def update_pose(self) -> None:
        """Update the robot pose."""
        if self.rotation is not None:
            self.imu_yaw = self.get_yaw()
            if self.imu_yaw is not None:
                self.imu_x += (self.robot.WHEEL_DIAMETER / 4) * (self.delta_left_encoder + self.delta_right_encoder) * math.cos(
                    self.imu_yaw)
                self.imu_y += (self.robot.WHEEL_DIAMETER / 4) * (self.delta_left_encoder + self.delta_right_encoder) * math.sin(
                    self.imu_yaw)


    def get_pose(self) -> tuple:
        """
        Return the current robot pose.

        Returns:
          The pose of the robot as a tuple: (x, y, heading).
            x = the cell x coordinate as integer,
            y = the cell y coordinate as integer,
            heading = the robot orientation: [0, 90, 180 or 270] or None.

          The heading follows the right-hand rule.
          The heading should account for heading_tolerance (+/-).
          E.g., if heading_tolerance=5 and actual robot heading is 88,
            the returned heading should be 90.
            If heading_tolerance=5 and actual robot heading is 84,
            the returned heading should be None.
            If heading_tolerance=5 and actual robot heading is 93,
            the returned heading should be 90.
          The heading = 0 means robot is facing down the x axis.
          The heading = 90 means robot is facing down the y axis.
          The heading = 180 means robot is facing down the -x axis.
          The heading = 270 means robot is facing down the -y axis.
          The heading = None if indeterminate
            (e.g., 45 degrees with +-5 degrees tolerance, 33 degrees)
            or heading is unknown.

        """
        if self.rotation is not None:
            return int(self.imu_x / self.cell_size), int(self.imu_y / self.cell_size), self.imu_yaw

    def get_yaw(self):
        """Make rotation into yaw"""
        adjusted_rotation = self.get_adjusted_rotation()
        if 360 - self.heading_tolerance < adjusted_rotation < self.heading_tolerance:
            return 0
        if 90 - self.heading_tolerance < adjusted_rotation < 90 + self.heading_tolerance:
            return 90
        if 180 - self.heading_tolerance < adjusted_rotation < 180 + self.heading_tolerance:
            return 180
        if 270 - self.heading_tolerance < adjusted_rotation < 270 + self.heading_tolerance:
            return 270

        return None


    def get_adjusted_rotation(self):
        """Normalize the found rotation"""
        return (self.initial_yaw + self.rotation) % 360


    def sense(self):
        """Define the SPA architecture sense block."""
        # Your code here...
        self.left_encoder = math.radians(self.robot.get_left_wheel_encoder())
        self.right_encoder = math.radians(self.robot.get_right_wheel_encoder())

        self.delta_left_encoder = self.left_encoder - self.last_left_encoder
        self.delta_right_encoder = self.right_encoder - self.last_right_encoder
        self.rotation = self.robot.get_rotation()

        self.last_left_encoder = self.left_encoder
        self.last_right_encoder = self.right_encoder



    def spin(self):
        """Spin the loop."""
        for _ in range(10):
            self.sense()
            self.update_pose()
            print(f"pose = {self.get_pose()}")
            self.robot.sleep(0.05)


def main():
    """Execute the spin."""
    robot = Robot(initial_odom=[0.16, 2.262, -1.57],
                  cell_size=0.3, heading_tolerance=5)
    robot.spin()


if __name__ == "__main__":
    main()