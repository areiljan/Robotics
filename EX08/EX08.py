"""EX08 - PID."""
import PiBot

class Robot:
    """The robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()
        self.previous_turn_right = 0
        self.previous_turn_left = 0
        self.current_turn_right = 0  # Setpoint
        self.current_turn_left = 0
        self.pid_power_right = 0
        self.pid_power_left = 0


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
        right_error_sum = 0
        left_error_sum = 0
        right_error = None
        left_error = None
        previous_right_error = None
        previous_left_error = None
        right_error_diff = 0
        left_error_diff = 0

        # Assign previous error
        if(right_error != None):
            previous_right_error = right_error
        if (left_error != None):
            previous_left_error = left_error


        # Used for proportional calculation
        right_error = self.right_setpoint - self.current_turn_right
        left_error = self.left_setpoint - self.current_turn_left

        # Integral term
        right_error_sum += right_error
        left_error_sum += left_error

        # Derivative term
        # Can only work if you have the previous value
        # If the controller does not have the previous value the derivative will be ignored
        if(previous_right_error):
            right_error_diff = right_error - previous_right_error
        if(previous_left_error):
            left_error_diff = left_error - previous_left_error


        self.pid_power_right = p * right_error + i * right_error_sum + d * right_error_diff
        self.pid_power_left = p * left_error + i * left_error_sum + d * left_error_diff


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
        self.current_turn_right = self.robot.get_right_wheel_encoder()
        self.current_turn_left = self.robot.get_left_wheel_encoder()



    def act(self):
        """Execute the SPA architecture act block."""
        # Your code here...
        pass

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