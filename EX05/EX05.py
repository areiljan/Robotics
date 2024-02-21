"""OT05 - Noise."""
import statistics

import PiBot


class Robot:
    """Robot class."""

    def __init__(self):
        """Initialize object."""
        self.front_middle_laser = None
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.filter = []
        self.laser_reading = None

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the PiBot reference."""
        self.robot = robot

    def get_front_middle_laser(self) -> float:
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        if self.laser_reading is not None:
            self.filter.append(self.laser_reading)
            if len(self.filter) > 5:
                self.filter.pop(0)
        if not self.filter:
            return None
        else:
            return statistics.median(self.filter)

    def sense(self):
        """Sense method as per SPA architecture."""
        self.laser_reading = self.robot.get_front_middle_laser()

    def spin(self):
        """Execute the spin loop."""
        while not self.shutdown:
            print(f'Value is {self.get_front_middle_laser()}')
            self.robot.sleep(0.05)
            if self.robot.get_time() > 20:
                self.shutdown = True


def main():
    """Execute the main spin loop."""
    robot = Robot()
    robot.spin()


if __name__ == "__main__":
    main()
