"""EX04 - Line tracking."""
import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.line_direction = 0

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

    def spin(self):
        """Execute the spin loop."""
        while not self.shutdown:
            timestamp = self.robot.get_time()
            print(f'timestamp is {timestamp}')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.shutdown = True

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


def test():
    """Test."""
    robot = Robot()
    import leaning_right
    data = leaning_right.get_data()
    robot.robot.load_data_profile(data)
    for i in range(999):
        print(f"left_encoder = {robot.robot.get_rightmost_line_sensor()}")
        robot.robot.sleep(0.05)


if __name__ == "__main__":
    test()