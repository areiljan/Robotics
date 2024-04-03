"""EX10 - Robot vision processing."""
import math
import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Initialize variables."""
        self.robot = PiBot.PiBot()
        self.resolution = self.robot.CAMERA_RESOLUTION  # (laius, kõrgus)
        self.FOV = self.robot.CAMERA_FIELD_OF_VIEW  # (horisontaalne laius kraadides, vertikaalne laius kraadides)

        self.objects = []

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the API reference."""
        self.robot = robot

    def get_closest_object(self):
        """Get closest object."""
        return max(self.objects, key=lambda x: x[2]) if len(self.objects) > 0 else ()

    def get_closest_visible_object_angle(self):
        """
        Find the closest visible object from the objects list.

        Returns:
          The angle (in radians) to the closest object w.r.t. the robot
          orientation (i.e., 0 is directly ahead) following the right
          hand rule (i.e., objects to the left have a plus sign and
          objects to the right have a minus sign).
          Must return None if no objects are visible.
        """
        degree_per_pixel = self.FOV[0] / self.resolution[0]
        closest_object = self.get_closest_object()
        camera_center_degrees = self.FOV[0] / 2

        if len(closest_object) > 0:
            object_x = closest_object[1][0]
            object_center_degrees = object_x * degree_per_pixel
            return math.radians(camera_center_degrees - object_center_degrees)
        return None

    def sense(self):
        """Define the SPA architecture sense block."""
        self.objects = self.robot.get_camera_objects()

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
