"""Be aMAZE."""

import PiBot

class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.state = "maze"

        self.left_wheel_speed = 13
        self.right_wheel_speed = 13
        self.right_acting_speed = 0
        self.left_acting_speed = 0

        self.right_diagonal_ir = None
        self.left_diagonal_ir = None
        self.last_right_diagonal_ir = 0
        self.last_left_diagonal_ir = 0
        self.none_seen_ticks = 0

        # For Calibration
        self.calibrated = False
        self.max_right_encoder = 0
        self.max_left_encoder = 0
        self.left_factor = 1
        self.right_factor = 1

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def drive_in_maze(self):
        """Stay inbetween walls and stop, when outside the maze."""
        if self.state == "maze":
            self.move_backward()
            print(self.right_diagonal_ir)
            print(self.left_diagonal_ir)
            if self.right_diagonal_ir > self.left_diagonal_ir:
                self.move_backward_right()
            elif self.right_diagonal_ir < self.left_diagonal_ir:
                self.move_backward_left()

            if (self.last_right_diagonal_ir == self.right_diagonal_ir
                    and self.last_left_diagonal_ir == self.left_diagonal_ir):
                self.none_seen_ticks += 1
                if self.none_seen_ticks == 15:
                    self.state = "idle"
            else:
                self.none_seen_ticks = 0

    def plan(self):
        """
        Check for state and activate functions accordingly.

        Use calibrate method for realism.
        Unknown is the state, where robot should do absolutely nothing.
        """
        if self.state == "maze":
            self.drive_in_maze()
        elif self.state == "idle":
            self.stop()

        self.last_right_diagonal_ir = self.right_diagonal_ir
        self.last_left_diagonal_ir = self.left_diagonal_ir

    def act(self):
        """Act according to plan."""
        self.robot.set_left_wheel_speed(self.left_acting_speed * self.left_factor)
        self.robot.set_right_wheel_speed(self.right_acting_speed * self.right_factor)

    def spin(self):
        """Start the main loop of the robot."""
        while not self.shutdown:
            self.sense()
            self.plan()
            self.act()
            self.robot.sleep(0.05)

    def calibrate(self):
        """Calibrate the robot."""
        self.left_wheel_speed = 20
        self.right_wheel_speed = 20
        if self.current_rotation < 360 * 3 and not self.calibrated:
            self.move_left_on_place()
            self.max_left_encoder = abs(self.current_left_encoder)
            self.max_right_encoder = abs(self.current_right_encoder)
        else:
            self.calibrated = True
            self.move_right_on_place()
            if self.max_right_encoder > self.max_left_encoder:
                self.left_factor = round(1 + (1 - self.max_left_encoder / self.max_right_encoder), 2)
            elif self.max_right_encoder < self.max_left_encoder:
                self.right_factor = round(1 + (1 - self.max_right_encoder / self.max_left_encoder), 2)

            self.stop()
            self.state = "look around"
            print("Corrections made", self.right_factor, self.left_factor)

    def sense(self):
        """Sense method as per SPA architecture."""
        self.right_diagonal_ir = self.robot.get_rear_right_diagonal_ir()
        self.left_diagonal_ir = self.robot.get_rear_left_diagonal_ir()

    def move_forward(self):
        """Set robot movement to forward."""
        self.left_acting_speed = self.left_wheel_speed
        self.right_acting_speed = self.right_wheel_speed

    def move_backward(self):
        """Set robot movement to backward."""
        self.left_acting_speed = -self.left_wheel_speed
        self.right_acting_speed = -self.right_wheel_speed

    def move_backward_right(self):
        """Set robot movement to right."""
        self.left_acting_speed = -self.left_wheel_speed + 3
        self.right_acting_speed = -self.right_wheel_speed

    def move_backward_left(self):
        """Set robot movement to left."""
        self.left_acting_speed = -self.left_wheel_speed
        self.right_acting_speed = -self.right_wheel_speed + 3

    def move_right_on_place(self):
        """Set robot movement to right."""
        self.left_acting_speed = self.left_wheel_speed
        self.right_acting_speed = -self.right_wheel_speed

    def move_left_on_place(self):
        """Set robot movement to left."""
        self.left_acting_speed = -self.left_wheel_speed
        self.right_acting_speed = self.right_wheel_speed

    def move_right(self):
        """Set robot movement to right."""
        self.left_acting_speed = self.left_wheel_speed
        self.right_acting_speed = -self.right_wheel_speed + 2

    def move_left(self):
        """Set robot movement to left."""
        self.left_acting_speed = -self.left_wheel_speed + 2
        self.right_acting_speed = self.right_wheel_speed

    def stop(self):
        """Set robot movement to stop."""
        self.left_acting_speed = 0
        self.right_acting_speed = 0


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
