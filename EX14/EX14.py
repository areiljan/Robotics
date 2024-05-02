"""EX13 - Mapping."""
import math

import PiBot


class Robot:
    """The robot class."""

    def __init__(self):
        """Class constructor."""
        self.robot = PiBot.PiBot()
        self.shutdown = False

        self.left_encoder = 0
        self.right_encoder = 0

        self.middle_laser = 0

        self.pose = [0, 0, 0]
        self.yaw = 0

        self.x_index = 1
        self.y_index = 1

        self.last_left_encoder = 0
        self.last_right_encoder = 0
        self.right_encoder_diff = 0
        self.left_encoder_diff = 0

        self.map = [["?", "?", "?"],
                    ["?", " ", "?"],
                    ["?", "?", "?"]]

    def set_robot(self, robot: PiBot.PiBot()) -> None:
        """Set the robot reference."""
        self.robot = robot

    def update_yaw(self, encoder_difference):
        """Update the yaw."""
        if encoder_difference == -2000:
            self.yaw += 90
        elif encoder_difference == 2000:
            self.yaw -= 90
            if self.yaw < 0:
                self.yaw = 360 + self.yaw

        self.yaw = self.yaw % 360

    def update_position(self, x, y):
        """Update existing position, by heading direction."""
        if self.yaw == 180:
            x -= 1
            self.x_index -= 2
        elif self.yaw == 0:
            x += 1
            self.x_index += 2
        elif self.yaw == 270:
            y -= 1
            self.y_index += 2
        elif self.yaw == 90:
            y += 1
            self.y_index -= 2
        return x, y

    def update_pose(self):
        """Update the robot pose using the sensor values."""
        self.left_encoder_diff = self.left_encoder - self.last_left_encoder
        self.right_encoder_diff = self.right_encoder - self.last_right_encoder

        encoder_difference = (self.left_encoder_diff - self.right_encoder_diff)
        self.update_yaw(encoder_difference)

        x = self.pose[0]
        y = self.pose[1]

        if encoder_difference == 0 and self.right_encoder_diff != 0 and self.left_encoder_diff != 0:
            x, y = self.update_position(x, y)

        self.pose = [x, y, self.yaw]

        self.last_left_encoder = self.left_encoder
        self.last_right_encoder = self.right_encoder

    def get_pose(self):
        """Return the pose as list, i.e [x, y, yaw]."""
        return self.pose

    def update_map(self) -> None:
        """Update the internal map using the sensor values."""
        self.modify_seen_blocks()
        self.minify_map()

    def add_column(self, right):
        """
        Add new column to the map.

        Also increments the x_index(robot position on mao), when looking left.
        """
        for row in self.map:
            if right:
                row.append("?")
            else:
                row.insert(0, "?")
        if not right:
            self.x_index += 1

    def add_row(self, down):
        """
        Add a new row to the map.

        Also increments the y_index (robot position on map), when looking up.
        """
        row_length = len(self.map[0])
        new_row = []
        for i in range(row_length):
            new_row.append("?")

        if down:
            self.map.append(new_row)
        else:
            self.map.insert(0, new_row)
            self.y_index += 1

    def remove_rows(self):
        """Try to remove unnecessary rows from map."""
        if " " not in self.map[1] and all(char == "?" for char in self.map[0]):
            self.y_index -= 1
            self.map.pop(0)

        if " " not in self.map[-2] and all(char == "?" for char in self.map[-1]):
            self.map.pop()

    def remove_columns(self):
        """Try to remove all unnecessary columns."""
        column1 = [row[0] for row in self.map]
        column2 = [row[1] for row in self.map]
        column3 = [row[-2] for row in self.map]
        column4 = [row[-1] for row in self.map]

        if " " not in column2 and all(char == "?" for char in column1):
            self.x_index -= 1
            self.remove_column(0)

        if " " not in column3 and all(char == "?" for char in column4):
            self.remove_column(-1)

    def minify_map(self):
        """Delete useless columns and rows."""
        for i in range(len(self.map)):
            self.remove_rows()
            self.remove_columns()

    def remove_column(self, i):
        """Remove a column by specific index."""
        new_map = []
        for row in self.map:
            row.pop(i)
            new_map.append(row)

        self.map = new_map

    def replace_character(self, x, y, character):
        """
        Replace character in the map.

        Removes the character only, when it isn't mapped already.
        """
        if self.map[y][x] == "?":
            self.map[y][x] = character

    def get_object_chars(self) -> list:
        """Decide by laser objects chars."""
        first_object = "?"
        second_object = "?"
        third_object = "?"
        fourth_object = "?"
        if self.middle_laser == 0:
            first_object = "X"
        elif self.middle_laser == 1:
            first_object = " "
            second_object = " "
            third_object = "X"
        elif self.middle_laser == 2:
            first_object = " "
            second_object = " "
            third_object = " "
            fourth_object = " "
        return [first_object, second_object, third_object, fourth_object]

    def modify_seen_blocks(self):
        """
        Replace all seen blocks with right character.

        Before replacing character rows or columns will be added.
        """
        objects = self.get_object_chars()

        yaw = self.pose[2]
        if yaw == 0:
            self.add_column(True)
            for i in range(1, 5):
                self.add_column(True)
                self.replace_character(self.x_index + i, self.y_index, objects[i - 1])
        elif yaw == 90:
            self.add_row(False)
            for i in range(1, 5):
                self.add_row(False)
                self.replace_character(self.x_index, self.y_index - i, objects[i - 1])
        elif yaw == 180:
            self.add_column(False)
            for i in range(1, 5):
                self.add_column(False)
                self.replace_character(self.x_index - i, self.y_index, objects[i - 1])
        elif yaw == 270:
            self.add_row(True)
            for i in range(1, 5):
                self.add_row(True)
                self.replace_character(self.x_index, self.y_index + i, objects[i - 1])

        self.replace_character(self.x_index, self.y_index, " ")

    def map_to_string(self):
        """Convert list into string."""
        string = ""
        for row in self.map:
            for char in row:
                string += char
            string += "\n"
        return string.strip()

    def get_map(self) -> str:
        """
        Print the known map.

        Returns:
          If no data has been gathered via sensors, must return None!

          The string representation of the map.
          Each cell should be one character + all neighboring cells/walls.
          The unknown spaces and walls should be denoted as "?"
          The walls should be marked as "X"

          An example:
            ?X?X???
            X   X??
            ? ? ?X?
            ? X   X
            ? ?X? ?
            ? X   X
            ? ? ?X?
            X   X??
            ?X?X???
        """
        if self.left_encoder == 0 and self.right_encoder == 0:
            return None

        return self.map_to_string()

    def find_closest_frontier(self) -> tuple:
        """
        Find the closest frontier.

        Returns:
          The cell coordinates as a tuple (x, y) with the best
          exploration value.
          The exploration value is defined as the Euclidean distance
          from the current robot position to the frontier (closer is better).
          A cell is considered to be a frontier if it has neighboring cells
          which have not been explored.
          In case of tiebreak, the frontier with more neighboring unknown
          cells must be preferred.
          If this does not break the tie, the cell which is farther
          from (0, 0) must be preferred.

          If there are no frontiers, return None.
        """
        # Return closer
        # Frontier with more neigbouring unknown cells
        # (0,0)
        tile_properties = {}
        robot_x, robot_y, yaw = self.pose
        for i, row in enumerate(self.map):
            for j, char in enumerate(row):
                if char == " ":
                    x, y = self.convert_map_index_to_world_coordinates(i, j)
                    unknown_tiles = self.count_neighbouring_unknown_tiles(i, j)
                    distance_from_robot = self.distance_between_tiles(x, y, robot_x, robot_y)
                    distance_from_zero_coordinate = self.distance_between_tiles(0, 0, x, y)

                    tile_properties[x, y] = [unknown_tiles, distance_from_robot, distance_from_zero_coordinate]

        sorted_data = sorted(tile_properties, key=lambda x: (x[0], x[1], x[2]))
        if sorted_data:
            return sorted_data[0]
        return None

    def convert_map_index_to_world_coordinates(self, x, y):
        """Convert map index to world coordinates"""
        new_x = x / 2
        new_y = y / 2
        return new_x, new_y


    def count_neighbouring_unknown_tiles(self, x, y):
        """Count the neighbouring unknown tiles for each empty space."""
        count = 0
        if self.map[x - 1][y] == "?":
            count += 1
        if self.map[x][y - 1] == "?":
            count += 1
        if self.map[x + 1][y] == "?":
            count += 1
        if self.map[x][y + 1] == "?":
            count += 1

        return count

    def distance_between_tiles(self, x1, y1, x2, y2):
        """Distance between two tiles."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


    def sense(self):
        """Define the SPA architecture sense method."""
        self.left_encoder = self.robot.get_left_wheel_encoder()
        self.right_encoder = self.robot.get_right_wheel_encoder()

        self.middle_laser = self.robot.get_front_middle_laser()


def main():
    """Execute the main loop."""
    robot = Robot()
    for i in range(100):
        robot.sense()
        robot.update_pose()
        robot.update_map()
        robot.robot.sleep(1)
    print(robot.get_map())


def test():
    """For testing purposes."""
    robot = Robot()
    import spinzag  # or any other data file
    data = spinzag.get_data()
    robot.robot.load_data_profile(data)
    for i in range(len(data)):
        print(f"laser = {robot.robot.get_front_middle_laser()}")
        robot.sense()
        robot.update_pose()
        robot.update_map()
        robot.robot.sleep(1)
    for row in robot.map:
        print(row)


if __name__ == "__main__":
    test()
