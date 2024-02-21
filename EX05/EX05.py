"""OT05 - Noise."""
import statistics

import PiBot
from queue import Queue


class Robot:
    """Robot class."""

    def __init__(self):
        """Initialize object."""
        self.robot = PiBot.PiBot()
        self.shutdown = False
        self.filter = Queue(maxsize=5)
        self.value = 0

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the PiBot reference."""
        self.robot = robot

    def get_front_middle_laser(self) -> float:
        """
        Return the filtered value.

        Returns:
          None if filter is empty, filtered value otherwise.
        """
        self.filter.append(self.robot.get_front_middle_laser())
        if self.filter == [] and self.front_middle_laser is None:
            return None
        if self.filter.full:
            self.filter.get()
        self.filter.append(self.front_middle_laser)
        return statistics.median(list(self.filter.queue))



    def sense(self):
        """Sense method as per SPA architecture."""
        self.value = self.robot.get_front_middle_laser()


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