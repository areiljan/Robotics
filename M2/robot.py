"""02."""
import math
import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

        # Wheel parameters
        self.wheel_circumference = self.robot.WHEEL_DIAMETER * math.pi
        self.machine_circumference = self.robot.AXIS_LENGTH * math.pi

        # Left wheel settings
        self.left_wheel_velocity = 8
        self.left_base_velocity = 0

        # Right wheel settings
        self.right_wheel_velocity = 8
        self.right_base_velocity = 0

        # Infrared sensor readings
        self.left_infrared = 0
        self.right_infrared = 0

        # Rotation settings
        self.current_rotation = 0
        self.rotation_setpoint = 0
        self.has_turned = False

        # Laser sensor reading
        self.front_laser_reading = 0

        # Other control parameters
        self.time_driven = 0
        self.state = "drive"

        # Thresholds and constants
        self.IR_THRESHOLD = 500
        self.LASER_THRESHOLD = 0.06
        self.TIME_TO_TURN = 100
        self.TIME_TO_FINISH = 40

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    def drive(self):
        """Drive the robot."""
        wall_in_front = self.front_laser_reading <= self.LASER_THRESHOLD and not self.has_turned

        if wall_in_front:
            # Check if there's no wall on the left side
            if self.left_infrared < self.IR_THRESHOLD:
                self.state = "left_turn"
            else:
                self.state = "right_turn"
            self.rotation_setpoint = self.current_rotation
        elif self.LASER_THRESHOLD < self.front_laser_reading < 2 and self.left_infrared < self.IR_THRESHOLD and not self.has_turned:
            self.no_wall_turn()
        else:
            self.drive_forward()

    def turn_left(self):
        """Turn left until facing left."""
        if self.current_rotation < self.rotation_setpoint + 90:
            self.move_left_on_place()
        else:
            self.complete_turn()

    def turn_right(self):
        """Turn right until facing right."""
        if self.current_rotation > self.rotation_setpoint - 90:
            self.move_right_on_place()
        else:
            self.complete_turn()

    def complete_turn(self):
        """Complete turn."""
        self.has_turned = True  # Robot has turned
        self.stop()
        self.state = "drive"

    def drive_forward(self):
        """Drive forward and check for signs of finish."""
        self.has_turned = self.left_infrared < self.IR_THRESHOLD

        if (self.front_laser_reading == 2 and self.has_turned
                and self.left_infrared < self.IR_THRESHOLD and self.right_infrared < self.IR_THRESHOLD):
            self.TIME_TO_FINISH -= 1  # a little hardcode
            if self.TIME_TO_FINISH == 0:
                self.state = "finish"

        # Move forward
        self.move_forward()

    def no_wall_turn(self):
        """Turn when not seeing a wall."""
        self.time_driven += 1  # Add time

        if self.time_driven == self.TIME_TO_TURN:  # Check the time driven, so robot can start turning if driven enough
            self.start_turn()

    def start_turn(self):
        """Start the 90-degree turn."""
        self.state = "left_turn"
        self.rotation_setpoint = self.current_rotation  # Capture the current rotation to make 90-degree turn
        self.time_driven = 0

    def finish(self):
        """Stop the robot, because it has made it to the finish."""
        self.stop()

    def move_forward(self):
        """Set robot movement to forward."""
        self.left_base_velocity = self.left_wheel_velocity
        self.right_base_velocity = self.right_wheel_velocity

    def move_right_on_place(self):
        """Set robot movement to right."""
        self.left_base_velocity = self.left_wheel_velocity
        self.right_base_velocity = -self.right_wheel_velocity

    def move_left_on_place(self):
        """Set robot movement to left."""
        self.left_base_velocity = -self.left_wheel_velocity
        self.right_base_velocity = self.right_wheel_velocity

    def stop(self):
        """Set robot movement to halt."""
        self.left_base_velocity = 0
        self.right_base_velocity = 0

    def sense(self):
        """Sense method as per SPA architecture."""
        self.left_infrared = round(self.robot.get_rear_left_side_ir())
        self.right_infrared = round(self.robot.get_rear_right_side_ir())
        self.front_laser_reading = self.robot.get_front_middle_laser()
        self.current_rotation = self.robot.get_rotation()

    def plan(self):
        """Plan the robots action."""
        if self.state == "drive":
            self.drive()
        if self.state == "left_turn":
            self.turn_left()
        if self.state == "right_turn":
            self.turn_right()
        if self.state == "finish":
            self.finish()

    def act(self):
        """Act according to plan."""
        self.robot.set_right_wheel_speed(self.right_base_velocity)
        self.robot.set_left_wheel_speed(self.left_base_velocity)

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
