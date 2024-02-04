"""Robot."""

import PiBot


class Robot:
    """Robot."""

    def __init__(self):
        """Initialize the robot."""
        self.robot = PiBot.PiBot()
        self.value = 0
        self.shutdown = False

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the reference to PiBot object."""
        self.robot = robot

    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        self.value = self.robot.get_front_middle_laser()


    def plan(self):
        """Detect the robots distance from the wall."""
        if self.value is None or self.value > 18:
            self.robot.act()
        else:
            self.robot.shutdown = True

    def act(self):
        """Drive the robot forwards."""
        self.robot.set_left_wheel_speed(10)
        self.robot.set_right_wheel_speed(10)


def main():
    """Create a Robot object and spin it."""
    robot = Robot()
    robot.spin()


def test():
    """Test."""
    robot = Robot()

    while not robot.shutdown:
        robot.sense()
        robot.plan()
        robot.robot.sleep(0.01)


if __name__ == "__main__":
    test()