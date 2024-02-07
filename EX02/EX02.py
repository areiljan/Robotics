"""Robot."""

import PiBot


class Robot:
    """Robot."""

    def __init__(self):
        """Initialize the robot."""
        self.robot = PiBot.PiBot()
        self.state = "unknown"
        self.value = 0
        self.shutdown = False

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the reference to PiBot object."""
        self.robot = robot

    def get_state(self) -> str:
        """Return the current state."""
        return self.state

    def sense(self):
        """Read values from sensors via PiBot  API into class variables (self)."""
        self.value = self.robot.get_front_middle_laser()

    def plan(self):
        """Perform the planning steps as required by the problem statement."""
        if self.value == 0:
            self.state = "unknown"
        if 0 < self.value <= 0.5:
            self.state = "close"
        if 0.5 < self.value <= 1.5:
            self.state = "ok"
        if 1.5 < self.value < 2.0:
            self.state = "far"
        if self.value >= 2.0:
            self.state = "very far"

    def spin(self):
        """Spin."""
        while not self.shutdown:
            print(f'The time is {self.robot.get_time()}!')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.sense()
                self.plan()
                self.shutdown = True


def main():
    """Create a Robot object and spin it."""
    robot = Robot()
    robot.spin()


def test():
    """Test."""
    robot = Robot()
    import forward_reverse
    data = forward_reverse.get_data()
    robot.robot.load_data_profile(data)
    for i in range(len(data)):
        robot.sense()
        robot.plan()
        print(f"middle_laser = {robot.robot.get_front_middle_laser()}")
        robot.robot.sleep(0.05)


if __name__ == "__main__":
    test()
