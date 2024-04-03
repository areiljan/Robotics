"""EX09 - Odometry."""
import PiBot
import math


class Robot:
    """Robot class."""

    def __init__(self, initial_odometry=[0, 0, 0]):
        """
        Initialize variables.

        Arguments:
          initial_odometry -- Initial odometry(start position and angle),
                              [x, y, yaw] in [meters, meters, radians]
        """
        self.robot = PiBot.PiBot()

        self.rotation = 0

        self.right_encoder = 0
        self.last_right_encoder = 0
        self.delta_right_encoder = 0

        self.left_encoder = 0
        self.last_left_encoder = 0
        self.delta_left_encoder = 0

        self.last_time = 0
        self.time = 0
        self.delta = 0

        self.encoder_x = initial_odometry[0]
        self.encoder_y = initial_odometry[1]
        self.encoder_yaw = initial_odometry[2]

        self.imu_x = initial_odometry[0]
        self.imu_y = initial_odometry[1]
        self.imu_yaw = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the API reference."""
        self.robot = robot

    def get_encoder_odometry(self):
        """
        Return the encoder odometry.

        Returns:
           A tuple with x, y coordinates and yaw angle (x, y, yaw)
           based on encoder data. The units must be (meters, meters, radians).
        """
        return self.encoder_x, self.encoder_y, self.encoder_yaw

    def get_imu_odometry(self):
        """
        Return the IMU odometry.

        Returns:
           A tuple with x, y coordinates and yaw angle (x, y, yaw)
           based on encoder and IMU data. The units must be
           (meters, meters, radians).
        """
        return self.imu_x, self.imu_y, self.imu_yaw

    def calculate_encoder_odometry(self):
        """Calculate the encoder odometry values."""
        self.encoder_yaw += (self.robot.WHEEL_DIAMETER / 2 / self.robot.AXIS_LENGTH) * (self.delta_right_encoder - self.delta_left_encoder)
        self.encoder_x += (self.robot.WHEEL_DIAMETER / 4) * (self.delta_left_encoder + self.delta_right_encoder) * math.cos(self.encoder_yaw)
        self.encoder_y += (self.robot.WHEEL_DIAMETER / 4) * (self.delta_left_encoder + self.delta_right_encoder) * math.sin(self.encoder_yaw)

    def calculate_imu_odometry(self):
        """Calculate the imu odometry values."""
        self.imu_yaw = self.rotation
        self.imu_x += (self.robot.WHEEL_DIAMETER / 4) * (self.delta_left_encoder + self.delta_right_encoder) * math.cos(self.imu_yaw)
        self.imu_y += (self.robot.WHEEL_DIAMETER / 4) * (self.delta_left_encoder + self.delta_right_encoder) * math.sin(self.imu_yaw)

    def sense(self):
        """Define the SPA architecture sense block."""
        self.time = self.robot.get_time()
        self.delta = self.time - self.last_time

        self.left_encoder = math.radians(self.robot.get_left_wheel_encoder())
        self.right_encoder = math.radians(self.robot.get_right_wheel_encoder())

        self.delta_left_encoder = self.left_encoder - self.last_left_encoder
        self.delta_right_encoder = self.right_encoder - self.last_right_encoder
        self.rotation = self.robot.get_rotation()

        self.calculate_encoder_odometry()
        self.calculate_imu_odometry()

        self.last_time = self.time
        self.last_left_encoder = self.left_encoder
        self.last_right_encoder = self.right_encoder

    def spin(self):
        """Spin loop."""
        for _ in range(100):
            self.sense()
            self.robot.sleep(0.05)


def main():
    """Execute the spin."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
