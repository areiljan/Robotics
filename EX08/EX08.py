"""EX08 - PID."""
import math

import PiBot

class Robot:
    """The robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()
        self.last_left_encoder = 0
        self.last_right_encoder = 0
        self.right_setpoint = 0
        self.left_setpoint = 0
        self.current_right_encoder = 0  # Setpoint
        self.current_left_encoder = 0
        self.pid_power_right = 0
        self.pid_power_left = 0
        self.radius = self.robot.WHEEL_DIAMETER / 2
        self.p = 0
        self.i = 0
        self.d = 0


    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the API reference."""
        self.robot = robot


    def set_pid_parameters(self, p: float, i: float, d: float):
        """
        Set the PID parameters.

        Arguments:
          p -- The proportional component.
          i -- The integral component.
          d -- The derivative component.
        """
        self.p = p
        self.i = i
        self.d = d


    def get_right_pid(self):
        """
        Calculate the right pid.
        :return:
        """
        right_error_sum = 0
        right_error = None
        previous_right_error = None
        right_error_diff = 0

        # Assign previous error
        if right_error is not None:
            previous_right_error = right_error

        # Used for Proportional calculation
        right_error = self.right_setpoint - self.get_right_wheel_pid_output();

        # Integral term
        right_error_sum += right_error

        # Derivative term
        # Can only work if you have the previous value
        # If the controller does not have the previous value the derivative will be ignored
        if previous_right_error:
            right_error_diff = right_error - previous_right_error

        if right_error_diff:
            self.pid_power_right = self.p * right_error + self.i * right_error_sum + self.d * right_error_diff

        return self.pid_power_right

    def get_left_pid(self):
        """
        Calculate the left pid.
        :return:
        """
        left_error_sum = 0
        left_error = None
        previous_left_error = None
        left_error_diff = 0

        # Assign previous error
        if left_error is not None:
            previous_left_error = left_error

        # Used for proportional calculation
        left_error = self.left_setpoint - self.get_left_velocity()

        # Integral term
        left_error_sum += left_error

        # Derivative term
        # Can only work if you have the previous value
        # If the controller does not have the previous value the derivative will be ignored
        if previous_left_error:
            left_error_diff = left_error - previous_left_error

        if left_error_diff:
            self.pid_power_left = self.p * left_error + self.i * left_error_sum + self.d * left_error_diff

        return self.pid_power_right

    def set_left_wheel_speed(self, speed: float):
        """
        Set the desired setpoint.

        Arguments:
          speed -- The speed setpoint for the controller.
        """
        self.left_setpoint = speed


    def set_right_wheel_speed(self, speed: float):
        """
        Set the desired setpoint.

        Arguments:
          speed -- The speed setpoint for the controller.
        """
        self.right_setpoint = speed


    def get_left_velocity(self) -> float:
        """
        Return the current left wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        left_displacement = (self.current_left_encoder - self.last_left_encoder) * math.pi / 180
        left_velocity = (left_displacement / 0.2) * self.radius
        self.last_left_encoder = self.current_left_encoder
        return left_velocity


    def get_right_velocity(self) -> float:
        """
        Return the current right wheel velocity.

        Returns:
          The current wheel translational velocity in meters per second.
        """
        right_displacement = (self.current_right_encoder - self.last_right_encoder) * math.pi / 180
        right_velocity = (right_displacement / 0.2) * self.radius
        self.last_right_encoder = self.current_right_encoder
        return right_velocity


    def get_left_wheel_pid_output(self):
        """
        Get the controller output value for the left motor.

        Returns:
          The controller output value.
        """
        return self.pid_power_left

    def get_right_wheel_pid_output(self):
        """
        Get the controller output value for the right motor.

        Returns:
          The controller output value.
        """
        return self.pid_power_right


    def sense(self):
        """Execute the SPA architecture sense block."""
        self.current_right_encoder = self.robot.get_right_wheel_encoder()
        self.current_left_encoder = self.robot.get_left_wheel_encoder()
        print("Left encode: " + str(self.current_left_encoder) + " Right encode: " + str(self.current_right_encoder))

    def act(self):
        """Execute the SPA architecture act block."""
        # Your code here...
        print("Left: " + str(self.get_left_velocity()) + " Right: " + str(self.get_right_velocity()))
        self.set_right_wheel_speed(self.get_right_pid())
        self.set_left_wheel_speed(self.get_left_pid())

    def spin(self):
        """Execute the spin loop."""
        for _ in range(200):
            self.sense()
            self.act()
            self.robot.sleep(0.20)


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.robot.set_coefficients(1.0, 0.7)
    robot.set_pid_parameters(0.1, 0.04, 0.001)
    robot.set_left_wheel_speed(400)  # degs/s
    robot.set_right_wheel_speed(400)  # degs/s
    robot.spin()


if __name__ == "__main__":
    main()