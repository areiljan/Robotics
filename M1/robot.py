"""Be aMAZEd"""
import statistics

import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.state = "look_around"

        self.left_wheel_speed = 10
        self.right_wheel_speed = 10
        self.right_acting_speed = 0
        self.left_acting_speed = 0

        self.current_rotation = 0

        self.current_right_encoder = 0
        self.current_left_encoder = 0

        self.left_laser = 2
        self.middle_laser = 2
        self.right_laser = 2
        self.left_laser_list = []
        self.middle_laser_list = []
        self.right_laser_list = []
        self.left_laser_median = 2
        self.middle_laser_median = 2
        self.right_laser_median = 2

        # For Calibration
        self.calibrated = False
        self.max_right_encoder = 0
        self.max_left_encoder = 0
        self.left_factor = 1
        self.right_factor = 1

        self.move_left_on_place()
    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def calculate_median(self):
        self.left_laser_list.append(self.left_laser)
        self.middle_laser_list.append(self.middle_laser)
        self.right_laser_list.append(self.right_laser)
        if len(self.middle_laser_list) > 5:
            self.left_laser_list.pop(0)
            self.middle_laser_list.pop(0)
            self.right_laser_list.pop(0)
        self.left_laser_median = statistics.median(self.left_laser_list)
        self.middle_laser_median = statistics.median(self.middle_laser_list)
        self.right_laser_median = statistics.median(self.right_laser_list)

    def look_around(self):
        if self.middle_laser_median > 0.2:
            self.move_forward()
            self.state = "drive_to_the_wall"

    def drive_to_the_wall(self):
        if self.middle_laser_median < 0.1:
            self.stop()
            if self.left_laser_median > self.right_laser_median:
                self.move_left_on_place()
            else:
                self.move_right_on_place()
            self.state = "drive_to_the_wall"

    def plan(self):
        """
        Check for state and activate functions accordingly.

        Use calibrate method for realism.
        Unknown is the state, where robot should do absolutely nothing.
        """
        self.calculate_median()

        if self.state == "calibrate":
            self.calibrate()
        elif self.state == "look_around":
            self.look_around()
        elif self.state == "drive_to_the_wall":
            self.drive_to_the_wall()

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

        self.left_laser = self.robot.get_front_left_laser()
        self.middle_laser = self.robot.get_front_middle_laser()
        self.right_laser = self.robot.get_front_right_laser()

    def move_forward(self):
        """Set robot movement to forward."""
        self.left_acting_speed = self.left_wheel_speed
        self.right_acting_speed = self.right_wheel_speed

    def move_backward(self):
        """Set robot movement to backward."""
        self.left_acting_speed = -self.left_wheel_speed
        self.right_acting_speed = -self.right_wheel_speed

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