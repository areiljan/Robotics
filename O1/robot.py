"""EX04 - Objects."""

import PiBot

class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.last = "forward"
        self.state = "calibrate"

        self.left_wheel_speed = 10
        self.right_wheel_speed = 10

        self.on_crossway = False
        self.direction_index = 0

        self.rightsecond_seen = None
        self.leftsecond_seen = None

        self.crossway_time_start = None

        self.last_rotation = 0

        self.current_right_encoder = 0
        self.current_left_encoder = 0

        self.max_right_encoder = 0
        self.max_left_encoder = 0

        self.left_factor = 1
        self.right_factor = 1

        self.calibrated = False

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def calibrate(self):
        """Calibrate the robot."""
        self.left_wheel_speed = 10
        self.right_wheel_speed = 10

        if self.max_right_encoder > self.max_left_encoder:
            self.left_factor = round(1 + (1 - self.max_left_encoder / self.max_right_encoder), 2)
            self.left_wheel_speed = round(20 * self.left_factor / 2)
        elif self.max_right_encoder < self.max_left_encoder:
            self.right_factor = round(1 + (1 - self.max_right_encoder / self.max_left_encoder), 2)
            self.right_wheel_speed = round(20 * self.right_factor / 2)

        print("Corrections made", self.right_factor, self.left_factor)

    def sense(self):
        """Sense method as per SPA architecture."""
        self.current_right_encoder = self.robot.get_right_wheel_encoder()
        self.current_left_encoder = self.robot.get_left_wheel_encoder()

        self.current_rotation = self.robot.get_rotation()

        self.time = self.robot.get_time()

    def move_forward(self):
        """Set robot movement to forward."""
        self.state = "forward"
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = self.right_wheel_speed

    def move_backward(self):
        """Set robot movement to backward."""
        self.state = "backward"
        self.left_base_speed = -self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed

    def move_right(self):
        """Set robot movement to right."""
        self.state = "right"
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed + 2 * self.right_factor

    def move_left(self):
        """Set robot movement to left."""
        self.state = "left"
        self.left_base_speed = -self.left_wheel_speed + 2 * self.left_factor
        self.right_base_speed = self.right_wheel_speed

    def move_right_on_place(self):
        """Set robot movement to right."""
        self.state = "right"
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed

    def move_left_on_place(self):
        """Set robot movement to left."""
        self.state = "left"
        self.left_base_speed = -self.left_wheel_speed
        self.right_base_speed = self.right_wheel_speed

    def normal_movement(self):
        """Operate on 'train' track, without crossways."""
        if self.leftsecond < 400:
            self.move_left()
        elif self.rightsecond < 400:
            self.move_right()
        elif self.leftthird < 400 or self.rightthird < 400:
            self.move_forward()
        elif self.rightmost < 400:
            self.move_right()
        elif self.leftmost < 400:
            self.move_left()
        else:
            if self.last == "right":
                self.move_right()
            else:
                self.move_left()

    def plan(self):
        """
        Return the direction of the line based on sensor readings.

        Returns:
          -1: Line is on the right (i.e., the robot should turn right to reach the line again)
           0: Robot is on the line (i.e., the robot should not turn to stay on the line) or no sensor info
           1: Line is on the left (i.e., the robot should turn left to reach the line again)
        """
        if self.state == "calibrate":
            print("i am in calibration mode please wait")
            self.left_wheel_speed = 20
            self.right_wheel_speed = 20
            if self.current_rotation < 360 * 3 and not self.calibrated:
                self.move_left_on_place()
                self.max_left_encoder = abs(self.current_left_encoder)
                self.max_right_encoder = abs(self.current_right_encoder)
            else:
                self.calibrated = True
                self.move_right_on_place()
                if self.current_rotation <= 0:
                    self.calibrate()
                    self.state = "unknown"
                    return
            self.state = "calibrate"
            return


    def act(self):
        """Act according to plan."""
        self.robot.set_left_wheel_speed(self.left_base_speed)
        self.robot.set_right_wheel_speed(self.right_base_speed)

    def spin(self):
        """Start the main loop of the robot."""
        while not self.shutdown:
            self.sense()
            self.plan()
            self.act()
            self.robot.sleep(0.05)


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()