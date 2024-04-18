"""O2 - Objects."""
import math
from typing import Optional
import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class initialization."""
        # ROBOT
        self.robot = PiBot.PiBot()
        self.shutdown = False

        # CONSTANTS
        self.wheel_circumference = self.robot.WHEEL_DIAMETER * math.pi
        self.machine_circumference = self.robot.AXIS_LENGTH * math.pi
        self.OBJECT_JUMP = 0.2
        self.ALLOWED_ERROR = 0.05

        # RIGHT ENCODER
        self.right_encoder = 0
        self.last_right_encoder = 0

        # LEFT ENCODER
        self.left_encoder = 0
        self.last_left_encoder = 0

        # ODOMETER
        self.x = 0
        self.y = 0
        self.yaw = 0

        # LEFT WHEEL
        self.left_wheel_speed = 8
        self.left_base_speed = 0
        self.left_factor = 1

        # RIGHT WHEEL
        self.right_wheel_speed = 8
        self.right_base_speed = 0
        self.right_factor = 1

        # LASER
        self.sensor_data = []
        self.middle_laser = 0

        # OBJECT FINDING
        self.rotation_before_finding = 0
        self.last_middle_laser = 0
        self.looking_at_object = False
        self.object_start = 0
        self.object_end = 0
        self.object_distance = 0
        self.objects = []

        # DRIVING TO OBJECT
        self.object_angle = 0
        self.turned_to_object = False

        # STATE
        self.state = "find_objects"

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set robot reference."""
        self.robot = robot

    # ------------------------------------------------------------
    # |                    PROBLEM SOLUTION                      |
    # ------------------------------------------------------------

    def get_front_middle_laser(self) -> Optional[float]:
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        return self.middle_laser

    def calculate_odometry(self):
        """Calculate the encoder odometry values."""
        delta_left_encoder = self.left_encoder - self.last_left_encoder
        delta_right_encoder = self.right_encoder - self.last_right_encoder
        self.x += (self.robot.WHEEL_DIAMETER / 4) * (delta_left_encoder + delta_right_encoder) * math.cos(math.radians(self.yaw))
        self.y += (self.robot.WHEEL_DIAMETER / 4) * (delta_left_encoder + delta_right_encoder) * math.sin(math.radians(self.yaw))

    def add_objects(self):
        """
        Return the list with the detected objects so far.

        (i.e., add new objects to the list as you detect them).

        Returns:
          The list with detected object angles, the angles are in
          degrees [0..360), 0 degrees being the start angle and following
          the right-hand rule (e.g., turning left 90 degrees is 90, turning
          right 90 degrees is 270 degrees).
        """
        middle_laser = self.get_front_middle_laser()

        # START OBJECT READING
        if abs(self.middle_laser - self.last_middle_laser) >= self.OBJECT_JUMP and not self.looking_at_object:
            self.object_start = self.yaw
            self.looking_at_object = True

        # END OBJECT READING
        elif abs(self.middle_laser - self.last_middle_laser) >= self.OBJECT_JUMP and self.looking_at_object:
            self.looking_at_object = False

            object_degrees = self.object_end - self.object_start  # Object with in degrees aka how many degrees robot saw object
            object_middle_radians = math.radians(self.object_end - (object_degrees / 2))  # Object middle point in radians from 0

            change_in_x = self.object_distance * math.cos(object_middle_radians)  # x value change to get to object x
            change_in_y = self.object_distance * math.sin(object_middle_radians)  # y value change to get to object y

            # OBJECT GLOBAL X AND Y
            object_x = self.x + change_in_x
            object_y = self.y + change_in_y

            self.objects.append((object_x, object_y))  # Add tuple of object x and y to objects list

            # RESETTING VALUES
            self.object_start = 0
            self.object_end = 0
            self.object_distance = 0

        # READING OBJECT
        elif self.looking_at_object:
            if middle_laser > self.object_distance:  # Getting the objects middle point distance
                self.object_distance = middle_laser

            self.object_end = self.yaw

        self.last_middle_laser = middle_laser

    def calculate_rectangles_fourth_coordinate(self, first_object, second_object, third_object):
        """Return the fourth object world coordinates."""
        x1, y1 = first_object
        x2, y2 = second_object
        x3, y3 = third_object

        side_vector_1 = (x2 - x1, y2 - y1)
        side_vector_2 = (x3 - x1, y3 - y1)

        x4 = x3 + side_vector_1[0] - side_vector_2[0]
        y4 = y3 + side_vector_1[1] - side_vector_2[1]

        return x4, y4

    def drive_to_point(self, x, y):
        if self.object_angle == 0:
            x_distance = x - self.x
            y_distance = y - self.y

            self.object_angle = math.degrees(math.atan2(y_distance, x_distance))
            print("turn" + str(self.object_angle))
        if not self.turned_to_object:
            if self.yaw > self.object_angle:
                self.move_right_on_place()
                print("turning")
            else:
                self.turned_to_object = True
                print("turned enough")
        else:
            if (x - self.ALLOWED_ERROR <= self.x <= x + self.ALLOWED_ERROR
                    and y - self.ALLOWED_ERROR <= self.y <= y + self.ALLOWED_ERROR):
                self.object_angle = 0
                print("I have arrived")
                return True
            else:
                self.move_forward()
                print(" x: " + self.x + " y: " + self.y)
                print("driving")
                return False

    def find_objects(self):
        """Find objects around robot."""
        if self.yaw < self.rotation_before_finding + 360:
            self.move_left_on_place()
            self.add_objects()
        else:
            self.stop()
            self.state = "move"

    def move(self):
        self.drive_to_point(self.objects[0][0], self.objects[0][1])

    # ------------------------------------------------------------
    # |                      MOVEMENT                            |
    # ------------------------------------------------------------

    def move_forward(self):
        """Set robot movement to forward."""
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = self.right_wheel_speed

    def move_backward(self):
        """Set robot movement to backward."""
        self.left_base_speed = -self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed

    def move_right(self):
        """Set robot movement to right."""
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed + 2 * self.right_factor

    def move_left(self):
        """Set robot movement to left."""
        self.left_base_speed = -self.left_wheel_speed + 2 * self.left_factor
        self.right_base_speed = self.right_wheel_speed

    def move_right_on_place(self):
        """Set robot movement to right."""
        self.left_base_speed = self.left_wheel_speed
        self.right_base_speed = -self.right_wheel_speed

    def move_left_on_place(self):
        """Set robot movement to left."""
        self.left_base_speed = -self.left_wheel_speed
        self.right_base_speed = self.right_wheel_speed

    def stop(self):
        """Set robot movement to halt."""
        self.left_base_speed = 0
        self.right_base_speed = 0

    # ------------------------------------------------------------
    # |                          SPA                             |
    # ------------------------------------------------------------
    def sense(self):
        """Sense method as per SPA architecture."""
        self.left_encoder = math.radians(self.robot.get_left_wheel_encoder())
        self.right_encoder = math.radians(self.robot.get_right_wheel_encoder())

        self.middle_laser = self.robot.get_front_middle_laser()

        self.yaw = self.robot.get_rotation()
        self.calculate_odometry()

        self.last_left_encoder = self.left_encoder
        self.last_right_encoder = self.right_encoder

    def plan(self):
        """
        Return the direction of the line based on sensor readings.

        Returns:
          -1: Line is on the right (i.e., the robot should turn right to reach the line again)
           0: Robot is on the line (i.e., the robot should not turn to stay on the line) or no sensor info
           1: Line is on the left (i.e., the robot should turn left to reach the line again)
        """
        if self.state == "find_objects":
            self.find_objects()
            print(self.objects)
        elif self.state == "move":
            self.move()

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


# ------------------------------------------------------------
# |                          MAIN                            |
# ------------------------------------------------------------


def main():
    """Execute the main loop."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()