"""EX04 - Line tracking."""
import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.line_direction = 0
        self.right_wheel = 0
        self.left_wheel = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def sense(self):
        """Sense method as per SPA architecture."""
        leftmost = self.robot.get_leftmost_line_sensor()
        second_from_left = self.robot.get_second_line_sensor_from_left()
        third_from_left = self.robot.get_third_line_sensor_from_left()
        third_from_right = self.robot.get_third_line_sensor_from_right()
        second_from_right = self.robot.get_second_line_sensor_from_right()
        rightmost = self.robot.get_rightmost_line_sensor()
        if third_from_left < 400 or third_from_right < 400:
            self.line_direction = 0
        elif leftmost < 400 or second_from_left < 400:
            self.line_direction = 1
        elif rightmost < 400 or second_from_right < 400:
            self.line_direction = -1

    def plan(self):
        """Plan."""
        if self.line_direction == 0:
            self.right_wheel = 8
            self.left_wheel = 8
        elif self.line_direction == 1:
            self.right_wheel = 10
            self.left_wheel = 6
        else:
            self.right_wheel = 6
            self.left_wheel = 10

    def act(self):
        """Act."""
        self.robot.set_left_wheel_speed(self.left_wheel)
        self.robot.set_right_wheel_speed(self.right_wheel)

    def spin(self):
        """Execute the spin loop."""
        while not self.shutdown:
            timestamp = self.robot.get_time()
            self.sense()
            self.plan()
            self.act()
            print(f'timestamp is {timestamp}')
            self.robot.sleep(0.05)

    def get_line_direction(self):
        """
        Return the direction of the line based on sensor readings.

        Returns:
          -1: Line is on the right (i.e., the robot should turn right to reach the line again)
           0: Robot is on the line (i.e., the robot should not turn to stay on the line) or no sensor info
           1: Line is on the left (i.e., the robot should turn left to reach the line again)
        """
        return self.line_direction


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
