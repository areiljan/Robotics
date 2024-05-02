"""Be aMAZEd"""
import statistics

import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.state = "unknown"

        self.left_wheel_speed = 10
        self.right_wheel_speed = 10
        self.right_acting_speed = 0
        self.left_acting_speed = 0

        self.current_rotation = 0

        self.current_right_encoder = 0
        self.current_left_encoder = 0

        self.right_side_ir = None
        self.left_side_ir = None


        # For Calibration
        self.calibrated = False
        self.max_right_encoder = 0
        self.max_left_encoder = 0
        self.left_factor = 1
        self.right_factor = 1


    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def plan(self):
        """
        Check for state and activate functions accordingly.

        Use calibrate method for realism.
        Unknown is the state, where robot should do absolutely nothing.
        """
        self.move_backward()
        print(self.right_side_ir)
        print(self.left_side_ir)
        if self.right_side_ir > self.left_side_ir:
            self.move_backward_right()
        else:
            self.move_backward_left()


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
        """Sense method according to the SPA architecture."""
        self.current_right_encoder = self.robot.get_right_wheel_encoder()
        self.current_left_encoder = self.robot.get_left_wheel_encoder()

        self.current_rotation = self.robot.get_rotation()
        self.right_side_ir = self.robot.get_rear_right_diagonal_ir()
        self.left_side_ir = self.robot.get_rear_left_diagonal_ir()



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
        self.left_acting_speed = self.left_wheel_speed - 2
        self.right_acting_speed = -self.right_wheel_speed

    def move_backward_left(self):
        """Set robot movement to left."""
        self.left_acting_speed = -self.left_wheel_speed
        self.right_acting_speed = self.right_wheel_speed - 2

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