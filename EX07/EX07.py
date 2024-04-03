"""EX07 - Driving in a Straight Line."""
import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()

        self.left_encoder = 0
        self.right_encoder = 0

        self.state = "calibrate"

        self.left_speed = 8
        self.right_speed = 8

        self.velocity_adjustment = 1

        self.count = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the robot reference."""
        self.robot = robot

    def set_state(self, state: str):
        """
        Set the current state.

        Arguments:
          state - the state as a string.
        """
        self.state = state

    def get_state(self) -> str:
        """
        Get the state.

        Returns:
          The state as a string.
        """
        return self.state

    def calibrate(self):
        """Calibrate robot movement."""
        if self.left_encoder > self.right_encoder:
            self.velocity_adjustment = (1 + (1 - self.right_encoder / self.left_encoder))
        elif self.left_encoder < self.right_encoder:
            self.velocity_adjustment = (1 + (1 - self.left_encoder / self.right_encoder))

    def sense(self):
        """Execute the sense method in the SPA architecture."""
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.right_encoder = self.robot.get_right_wheel_encoder()

    def plan(self):
        """Execute the plan method in the SPA architecture."""
        if self.left_encoder == 0 == self.right_encoder:
            pass

        if self.state == "calibrate":
            if self.count != 80:
                self.count += 1
            else:
                self.calibrate()
                self.set_state("ready")
        elif self.state == "ready":
            self.set_state("drive")
        elif self.state == "drive":
            self.left_speed = 8
            self.right_speed = 8
            if self.left_encoder > self.right_encoder:
                self.right_speed *= self.velocity_adjustment
            else:
                self.left_speed *= self.velocity_adjustment
            self.calibrate()

    def act(self):
        """Execute the act method in the SPA architecture."""
        self.robot.set_left_wheel_speed(self.left_speed)
        self.robot.set_right_wheel_speed(self.right_speed)


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.robot.set_coefficients(0.7, 1.0)
    robot.set_state("calibrate")
    for i in range(int(120 / 0.05)):
        if robot.get_state() == "ready":
            start_left = robot.robot.get_left_wheel_encoder()
            start_right = robot.robot.get_right_wheel_encoder()
            robot.set_state("drive")
        robot.sense()
        robot.plan()
        robot.act()
        robot.robot.sleep(0.05)
    left_delta = robot.robot.get_left_wheel_encoder() - start_left
    right_delta = robot.robot.get_right_wheel_encoder() - start_right
    print(f"left {left_delta} right {right_delta}")


if __name__ == "__main__":
    main()