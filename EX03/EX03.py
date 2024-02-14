"""EX03 - Instantaneous velocity."""
import PiBot
import math


class Robot:
    """The robot class."""

    def __init__(self):
        """Class constructor."""
        self.total_turn_left = None
        self.total_turn_right = None
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.time = 0
        self.timestamp = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def get_left_velocity(self) -> float:
        """
        Return the current left wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        wheel_diameter = self.robot.WHEEL_DIAMETER
        wheel_circumference = wheel_diameter * math.pi
        left_difference = self.total_turn_left - self.robot.get_left_wheel_encoder()
        time = self.robot.get_time() - self.timestamp
        left_velocity = ((left_difference * wheel_circumference) / 360) / time
        return left_velocity

    def get_right_velocity(self) -> float:
        """
        Return the current right wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        wheel_diameter = self.robot.WHEEL_DIAMETER
        wheel_circumference = wheel_diameter * math.pi
        right_difference = self.total_turn_right - self.robot.get_right_wheel_encoder()
        time = self.robot.get_time() - self.timestamp
        right_velocity = ((right_difference * wheel_circumference) / 360) / time
        return right_velocity

    def sense(self):
        """Read the sensor values from the PiBot API."""
        # Your code here...
        self.total_turn_right = self.robot.get_right_wheel_encoder()
        self.total_turn_left = self.robot.get_left_wheel_encoder()

    def spin(self):
        """Spin."""
        while not self.shutdown:
            self.sense()
            self.timestamp = self.robot.get_time()
            left_velocity = self.get_left_velocity()
            right_velocity = self.get_right_velocity()
            print(f'{self.timestamp}: {left_velocity} {right_velocity}')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.shutdown = True


def main():
    """Test."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()