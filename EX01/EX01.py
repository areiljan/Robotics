"""Robot."""

import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Initialize class."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """
        Set the reference to the robot instance.

        NB! This is required for automatic testing.
        You are not expected to call this method in your code.

        Arguments:
          robot -- the reference to the robot instance.
        """
        self.robot = robot

    def spin(self):
        """Call sense, plan, act methods cyclically."""
        while not self.shutdown:
            print(f'The time is {self.robot.get_time()}!')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.shutdown = True

    def sense(self):
        """Sense."""

    def plan(self):
        """Plan."""

    def act(self):
        """Act."""


def main():
    """Create a Robot class object and run it."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()