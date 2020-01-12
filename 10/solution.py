from math import gcd, atan2, degrees


class Path:
    def __init__(self, dx, dy, finalx, finaly):
        self.dx = dx
        self.dy = dy
        self.finalx = finalx
        self.finaly = finaly
        self.degrees = degrees(atan2(dy, dx))
        if self.degrees < 0:
            '''full 360 degrees'''
            self.degrees = 360 + self.degrees

    def __hash__(self):
        return hash((self.dx, self.dy))

    def __eq__(self, other):
        return self.dx == other.dx and self.dy == other.dy

    def __lt__(self, other):
        '''we compare in clockwise order'''
        left = self.degrees
        if left <= 90:
            left = 90 + 360
        right = other.degrees
        if right <= 90:
            right = 90 + 360
        return left < right


def solve(input_string):
    space = []
    for row in input_string.split("\n"):
        space.append([True if char == "#" else False for char in row])

    def findAllPathsToAsteroidsFromPosition(origin_x, origin_y):
        paths = {}
        for y, row in enumerate(space):
            for x, cell in enumerate(row):
                distance = abs(y - origin_y) + abs(x - origin_x)
                if cell == True and distance != 0:
                    # find reduced dx/dy
                    dx = x - origin_x
                    dy = origin_y - y
                    d = gcd(dx, dy)
                    dx = dx // d
                    dy = dy // d
                    path = Path(dx, dy, x, y)

                    # add to paths map, if shortest distance for that path
                    if path not in paths or paths[path] > distance:
                        paths[path] = distance
        return paths

    max_asteroids_detected = 0
    monitoring_station_x = 0
    monitoring_station_y = 0

    # find ideal location where we can detect the most asteroids
    for y, row in enumerate(space):
        for x, cell in enumerate(row):
            if cell == True:
                paths = findAllPathsToAsteroidsFromPosition(x, y)
                if len(paths) > max_asteroids_detected:
                    max_asteroids_detected = len(paths)
                    monitoring_station_x = x
                    monitoring_station_y = y

    print(max_asteroids_detected)

    # from that location, start to destroy asteroids in a clockwise rotation until we get to the 200th
    total_destroyed = 0
    x_of_200 = 0
    y_of_200 = 0
    while x_of_200 == 0 and y_of_200 == 0:
        paths = findAllPathsToAsteroidsFromPosition(monitoring_station_x,
                                                    monitoring_station_y)

        paths = list(paths.keys())
        # TODO: fix clockwise sort
        paths.sort(reverse=True)

        # in clockwise order, destroy them
        for path in paths:
            x = path.finalx
            y = path.finaly
            total_destroyed += 1
            space[y][x] = False
            if total_destroyed == 200:
                x_of_200 = x
                y_of_200 = y
                break

    print((x_of_200 * 100) + y_of_200)

    return


solve("""#.#.###.#.#....#..##.#....
.....#..#..#..#.#..#.....#
.##.##.##.##.##..#...#...#
#.#...#.#####...###.#.#.#.
.#####.###.#.#.####.#####.
#.#.#.##.#.##...####.#.##.
##....###..#.#..#..#..###.
..##....#.#...##.#.#...###
#.....#.#######..##.##.#..
#.###.#..###.#.#..##.....#
##.#.#.##.#......#####..##
#..##.#.##..###.##.###..##
#..#.###...#.#...#..#.##.#
.#..#.#....###.#.#..##.#.#
#.##.#####..###...#.###.##
#...##..#..##.##.#.##..###
#.#.###.###.....####.##..#
######....#.##....###.#..#
..##.#.####.....###..##.#.
#..#..#...#.####..######..
#####.##...#.#....#....#.#
.#####.##.#.#####..##.#...
#..##..##.#.##.##.####..##
.##..####..#..####.#######
#.#..#.##.#.######....##..
.#.##.##.####......#.##.##""")