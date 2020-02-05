import sys, os
from typing import Tuple
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from intcode import IntcodeComputerV2 as IntcodeComputer

RiseAndRun = Tuple[int, int]


class InputModule:
    def __init__(self, x, y):
        self.input_sequence = [x, y]
        return

    def __call__(self):
        return self.input_sequence.pop(0)


class OutputModule:
    def __init__(self):
        return

    def __call__(self, number, intcode):
        self.result = number
        return


# https://stackoverflow.com/a/31818069/3529744
def proper_round(num, dec=0):
    num = str(num)[:str(num).index('.') + dec + 2]
    if num[-1] >= '5':
        return float(num[:-2 - (not dec)] + str(int(num[-2 - (not dec)]) + 1))
    return float(num[:-1])


def getRiseAndRunOfPoints(points):
    riseOverRuns = []
    for i, point1 in enumerate(points):
        for j in range(i, len(points)):
            point2 = points[j]
            if point2[0] != point1[0]:
                riseOverRuns.append(
                    (point2[1] - point1[1]) / (point2[0] - point1[0]))
    return proper_round(sum(riseOverRuns) / len(riseOverRuns))


def printCoordinates(coordinates_to_check, max_x, max_y):
    for y in range(0, max_y):
        row = []
        for x in range(0, max_x):
            if (x, y) in coordinates_to_check:
                result = coordinates_to_check[(x, y)]
            else:
                result = 0
            row.append(result)
        print(''.join(['#' if result == 1 else '.' for result in row]))
    return


def checkCoordinates(program, x, y):
    input_handler = InputModule(x, y)
    output_handler = OutputModule()
    intcodeComputer = IntcodeComputer(program,
                                      input_handler=input_handler,
                                      output_handler=output_handler)
    intcodeComputer.run()
    result = output_handler.result
    return result


def getTotalAffectedPointsInRange(program, x_range, y_range):
    x_range = 50
    y_range = 50

    coordinates_to_check = {}
    total_affected = 0
    first_ones = []
    last_ones = []
    for y in range(0, y_range):
        for x in range(0, x_range):
            result = checkCoordinates(program, x, y)
            if result == 1:
                total_affected += 1
            coordinates_to_check[(x, y)] = result

    return total_affected


def solve(puzzle_input):
    program = puzzle_input

    # print(getTotalAffectedPointsInRange(puzzle_input, 50, 50))

    # let's try to find a 100x100 range
    range_width = 100
    range_height = 100

    # let's start a little further down
    x = 0
    y = range_height

    top_left_corner = None
    while top_left_corner is None:
        print("{},{}".format(x, y), end='\r')
        result = checkCoordinates(program, x, y)
        if result == 1:
            # ok let's jump forward to at least the x + RANGE_WIDTH - 1 space
            if checkCoordinates(program, x + range_width - 1, y) == 0:
                # couldn't be this line, go down
                y += 1
                continue
            else:
                # this could be the line where it starts, let's try
                range_y_start = y
                range_x_start = x
                while True:
                    # walk until we find a 1 (this should be the potential bottom left corner)
                    if checkCoordinates(program, range_x_start,
                                        range_y_start + range_height - 1) == 0:
                        range_x_start += 1
                        continue

                    # check if top_right_corner is also a 1
                    top_right_corner = checkCoordinates(
                        program, range_x_start + range_width - 1,
                        range_y_start)

                    if top_right_corner == 1:
                        top_left_corner = (range_x_start, range_y_start)
                    break
        x += 1

    print((top_left_corner[0] * 10000) + top_left_corner[1])
    return


solve(
    """109,424,203,1,21101,11,0,0,1105,1,282,21102,1,18,0,1105,1,259,1201,1,0,221,203,1,21102,31,1,0,1106,0,282,21101,38,0,0,1106,0,259,21001,23,0,2,22102,1,1,3,21101,0,1,1,21102,57,1,0,1106,0,303,1202,1,1,222,20102,1,221,3,21002,221,1,2,21101,259,0,1,21102,80,1,0,1106,0,225,21101,0,51,2,21101,0,91,0,1106,0,303,1202,1,1,223,20101,0,222,4,21101,259,0,3,21102,225,1,2,21101,225,0,1,21101,118,0,0,1105,1,225,20102,1,222,3,21102,1,152,2,21102,133,1,0,1105,1,303,21202,1,-1,1,22001,223,1,1,21102,1,148,0,1105,1,259,1202,1,1,223,20101,0,221,4,21002,222,1,3,21102,1,17,2,1001,132,-2,224,1002,224,2,224,1001,224,3,224,1002,132,-1,132,1,224,132,224,21001,224,1,1,21101,195,0,0,105,1,108,20207,1,223,2,21002,23,1,1,21102,1,-1,3,21102,214,1,0,1105,1,303,22101,1,1,1,204,1,99,0,0,0,0,109,5,1202,-4,1,249,22101,0,-3,1,21202,-2,1,2,22102,1,-1,3,21101,250,0,0,1106,0,225,22101,0,1,-4,109,-5,2105,1,0,109,3,22107,0,-2,-1,21202,-1,2,-1,21201,-1,-1,-1,22202,-1,-2,-2,109,-3,2106,0,0,109,3,21207,-2,0,-1,1206,-1,294,104,0,99,22101,0,-2,-2,109,-3,2105,1,0,109,5,22207,-3,-4,-1,1206,-1,346,22201,-4,-3,-4,21202,-3,-1,-1,22201,-4,-1,2,21202,2,-1,-1,22201,-4,-1,1,21201,-2,0,3,21102,1,343,0,1105,1,303,1106,0,415,22207,-2,-3,-1,1206,-1,387,22201,-3,-2,-3,21202,-2,-1,-1,22201,-3,-1,3,21202,3,-1,-1,22201,-3,-1,2,21202,-4,1,1,21102,1,384,0,1105,1,303,1105,1,415,21202,-4,-1,-4,22201,-4,-3,-4,22202,-3,-2,-2,22202,-2,-4,-4,22202,-3,-2,-3,21202,-4,-1,-2,22201,-3,-2,1,22102,1,1,-4,109,-5,2105,1,0"""
)
