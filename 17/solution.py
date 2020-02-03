import sys, os
from enum import Enum
from typing import Tuple, List
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from intcode import IntcodeComputerV2 as IntcodeComputer


class Turn(Enum):
    NONE = 0
    LEFT = -1
    RIGHT = 1


class Direction(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4


Cell = Tuple[int, int]  # (x,y)
PathNode = Tuple[Cell, Turn]
Path = List[PathNode]


def getFinalCommandForMovementPattern(pattern):
    parts = []
    for movement in pattern:
        turn = movement[0]
        walk = movement[1:]
        parts.append(turn)
        parts.append(walk)
    final_command = ','.join(parts)
    return final_command


def doesPatternMatch(move_commands, pattern, index):
    '''can we match the given pattern to the given start location'''
    if index + len(pattern) > len(move_commands):
        '''pattern is to long, not enough room at end of list'''
        return False
    return move_commands[index:index + len(pattern)] == pattern


def findFirstNonMatchingIndex(move_commands, patterns, start_index):
    '''provide our patterns and see if we can find any sub-section that does not match'''
    while start_index < len(move_commands):
        found_match = False
        for pattern in patterns:
            if doesPatternMatch(move_commands, pattern, start_index):
                '''great, one of our patterns works, move forward to next start location'''
                start_index += len(pattern)
                found_match = True
                break
        if not found_match:
            '''none of our patterns worked at this position'''
            return start_index
    return -1


def choosePatterns(move_commands, start_index, patterns: List[List[str]],
                   count):
    if len(patterns) == count:
        # see if we match all
        return findFirstNonMatchingIndex(move_commands, patterns, 0) == -1
    current_index = start_index
    while current_index < len(move_commands):
        offset = 0

        # if we already have a working pattern for this, skip forward
        found_pattern_already_matching = None
        for pattern in patterns:
            if doesPatternMatch(move_commands, pattern, start_index):
                found_pattern_already_matching = pattern
                break
        if found_pattern_already_matching:
            offset += len(found_pattern_already_matching)

        current_index += 1
        pattern = move_commands[offset + start_index:offset + current_index]
        if len(getFinalCommandForMovementPattern(pattern)) > 20:
            '''final movement command cannot be longer than 20 '''
            continue
        if pattern in patterns:
            '''already have that patterns'''
            continue
        patterns.append(pattern)
        patterns.sort(key=len, reverse=True)
        matched = choosePatterns(move_commands, current_index + offset,
                                 patterns, count)
        if matched:
            return True
        else:
            patterns.remove(pattern)

    return False


def determineTurn(start_direction: Direction,
                  end_direction: Direction) -> Turn:
    if end_direction.value > start_direction.value:
        if end_direction.value == 4 and start_direction.value == 1:
            return Turn.LEFT
        return Turn.RIGHT
    else:
        if end_direction.value == 1 and start_direction.value == 4:
            return Turn.RIGHT
        return Turn.LEFT


def getRelativeDirection(start_cell: Cell, stop_cell: Cell) -> Direction:
    if start_cell == stop_cell:
        raise Exception("Start and stop cells are the same {}", start_cell)
    if start_cell[0] == stop_cell[0]:
        # same column
        if start_cell[1] < stop_cell[1]:
            return Direction.SOUTH
        elif start_cell[1] > stop_cell[1]:
            return Direction.NORTH
    if start_cell[1] == stop_cell[1]:
        # same row
        if start_cell[0] < stop_cell[0]:
            return Direction.EAST
        elif start_cell[0] > stop_cell[0]:
            return Direction.WEST
    raise Exception("Unable to find direction between {} and {}".format(
        start_cell, stop_cell))


def getCellInDirection(start_cell: Cell, direction: Direction) -> Cell:
    if direction == Direction.WEST:
        return (start_cell[0] - 1, start_cell[1])
    if direction == Direction.EAST:
        return (start_cell[0] + 1, start_cell[1])
    if direction == Direction.NORTH:
        return (start_cell[0], start_cell[1] - 1)
    if direction == Direction.SOUTH:
        return (start_cell[0], start_cell[1] + 1)
    raise Exception("Invalid direction: {}".format(direction))


class Input:
    def __init__(self, input_string):
        if input_string:
            self.input_array = [ord(i) for i in input_string]
        return

    def __call__(self):
        input_number = self.input_array.pop(0)
        print(chr(input_number), end='')
        return input_number


class Output:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.scaffoldings = set()
        return

    def __call__(self, number, intcode):

        # special things to track
        if number == 94:
            self.robot = (self.x, self.y)
        elif number == 35:
            self.scaffoldings.add((self.x, self.y))

        if number == 10:
            self.y += 1
            self.x = 0
        else:
            self.x += 1

        if number > 128:
            print(str(number))
        else:
            print(chr(number), end='')

        return

    def getScaffoldingsAdjacent(self, cell: Cell) -> List[Cell]:
        adjacent_cells = []
        if (cell[0] + 1, cell[1]) in self.scaffoldings:
            adjacent_cells.append((cell[0] + 1, cell[1]))
        if (cell[0], cell[1] + 1) in self.scaffoldings:
            adjacent_cells.append((cell[0], cell[1] + 1))
        if (cell[0] - 1, cell[1]) in self.scaffoldings:
            adjacent_cells.append((cell[0] - 1, cell[1]))
        if (cell[0], cell[1] - 1) in self.scaffoldings:
            adjacent_cells.append((cell[0], cell[1] - 1))
        return adjacent_cells

    def getPathOfScaffold(self) -> Path:
        '''
        Walk the path of the scaffolding from where the robot is, until we reach the end
        '''

        path: Path = []

        # start at robot
        current_cell = self.robot
        direction = None

        # i honestly just hardcoded the turn here
        path.append(((current_cell[0], current_cell[1]), Turn.LEFT))

        while True:

            next_expected = None
            if not direction:
                # we must be starting, let's find out what direction to go
                adjacent_cells = self.getScaffoldingsAdjacent(current_cell)
                if len(adjacent_cells) != 1:
                    raise Exception("Could not find a cell adjacent to {}",
                                    current_cell)
                direction = getRelativeDirection(self.robot, adjacent_cells[0])
                next_expected = adjacent_cells[0]
            else:
                next_expected = getCellInDirection(current_cell, direction)

            if next_expected in self.scaffoldings:
                # keep going
                path.append(((next_expected[0], next_expected[1]), Turn.NONE))
                current_cell = next_expected
            else:
                # look around for next direction
                adjacent_spaces = self.getScaffoldingsAdjacent(current_cell)

                if len(adjacent_spaces) == 1:
                    # we're done!
                    break

                for adjacent_space in adjacent_spaces:
                    adjacent_direction = getRelativeDirection(
                        current_cell, adjacent_space)
                    if abs(direction.value - adjacent_direction.value) != 2:
                        # it is not behind us, so we are turning now

                        turn = determineTurn(direction, adjacent_direction)

                        current_cell = adjacent_space
                        direction = adjacent_direction
                        path.append(((current_cell[0], current_cell[1]), turn))
                        break

        return path


def solve(puzzle_input):
    puzzle_input = puzzle_input.strip()
    output = Output()
    intcodeComputer = IntcodeComputer(puzzle_input,
                                      input_handler=Input(None),
                                      output_handler=output)
    intcodeComputer.run()
    path = output.getPathOfScaffold()

    def getTotalAlignmentParameters(path):
        intersections = set()
        visited = set()
        for cell in path:
            if cell[0] in visited:
                intersections.add(cell[0])
            visited.add(cell[0])

        total_alignment_parameters = 0
        for intersection in intersections:
            total_alignment_parameters += intersection[0] * intersection[1]
        return total_alignment_parameters

    def moveRobot(puzzle_input, path):
        # transform path into series of movements
        turn = path[0][1]
        steps = 0
        move_commands = []
        for i, node in enumerate(path[1:]):
            if node[1] != Turn.NONE or i == len(path) - 2:
                if i == len(path) - 2:
                    steps += 1
                # starting new segment
                move_commands.append(('R' if turn == Turn.RIGHT else 'L') +
                                     str(steps))
                steps = 1
                turn = node[1]
            else:
                steps += 1

        # look for patterns, decide on A, B, and C routines
        patterns = []
        choosePatterns(move_commands, 0, patterns, 3)

        # decide what order patterns should go in
        start_index = 0
        pattern_order = []
        while start_index < len(move_commands):
            found_pattern = False
            sub_commands = move_commands[start_index:]
            for pattern_index, pattern in enumerate(patterns):
                if len(pattern) <= len(sub_commands) and sub_commands[:len(
                        pattern)] == pattern:
                    pattern_order.append(pattern_index)
                    start_index += len(pattern)
                    found_pattern = True
                    break
            if not found_pattern:
                raise Exception(
                    "Unable to find matching pattern for commands {} starting at {} with patterns {}"
                    .format(move_commands, start_index, patterns))

        # generate actual input
        robot_input = []
        robot_input.append(','.join([chr(i + 65) for i in pattern_order]))
        for pattern in patterns:
            robot_input.append(getFinalCommandForMovementPattern(pattern))
        robot_input = '\n'.join(robot_input) + '\nn\n'
        print(robot_input)

        # RERUN!
        puzzle_input = puzzle_input.strip()
        output = Output()
        intcodeComputer = IntcodeComputer(puzzle_input,
                                          input_handler=Input(robot_input),
                                          output_handler=output)
        intcodeComputer.memory[0] = 2
        intcodeComputer.run()
        path = output.getPathOfScaffold()

    print(getTotalAlignmentParameters(path))
    print(moveRobot(puzzle_input, path))

    return


solve("""
1,330,331,332,109,3016,1101,1182,0,16,1101,1441,0,24,102,1,0,570,1006,570,36,1002,571,1,0,1001,570,-1,570,1001,24,1,24,1106,0,18,1008,571,0,571,1001,16,1,16,1008,16,1441,570,1006,570,14,21101,58,0,0,1105,1,786,1006,332,62,99,21101,333,0,1,21101,73,0,0,1105,1,579,1101,0,0,572,1101,0,0,573,3,574,101,1,573,573,1007,574,65,570,1005,570,151,107,67,574,570,1005,570,151,1001,574,-64,574,1002,574,-1,574,1001,572,1,572,1007,572,11,570,1006,570,165,101,1182,572,127,102,1,574,0,3,574,101,1,573,573,1008,574,10,570,1005,570,189,1008,574,44,570,1006,570,158,1106,0,81,21101,340,0,1,1106,0,177,21102,1,477,1,1106,0,177,21101,514,0,1,21102,176,1,0,1105,1,579,99,21102,1,184,0,1105,1,579,4,574,104,10,99,1007,573,22,570,1006,570,165,1002,572,1,1182,21101,0,375,1,21101,211,0,0,1105,1,579,21101,1182,11,1,21101,222,0,0,1105,1,979,21102,1,388,1,21102,1,233,0,1105,1,579,21101,1182,22,1,21102,244,1,0,1106,0,979,21102,401,1,1,21101,0,255,0,1106,0,579,21101,1182,33,1,21101,266,0,0,1106,0,979,21102,414,1,1,21101,0,277,0,1105,1,579,3,575,1008,575,89,570,1008,575,121,575,1,575,570,575,3,574,1008,574,10,570,1006,570,291,104,10,21102,1,1182,1,21101,0,313,0,1106,0,622,1005,575,327,1102,1,1,575,21101,327,0,0,1106,0,786,4,438,99,0,1,1,6,77,97,105,110,58,10,33,10,69,120,112,101,99,116,101,100,32,102,117,110,99,116,105,111,110,32,110,97,109,101,32,98,117,116,32,103,111,116,58,32,0,12,70,117,110,99,116,105,111,110,32,65,58,10,12,70,117,110,99,116,105,111,110,32,66,58,10,12,70,117,110,99,116,105,111,110,32,67,58,10,23,67,111,110,116,105,110,117,111,117,115,32,118,105,100,101,111,32,102,101,101,100,63,10,0,37,10,69,120,112,101,99,116,101,100,32,82,44,32,76,44,32,111,114,32,100,105,115,116,97,110,99,101,32,98,117,116,32,103,111,116,58,32,36,10,69,120,112,101,99,116,101,100,32,99,111,109,109,97,32,111,114,32,110,101,119,108,105,110,101,32,98,117,116,32,103,111,116,58,32,43,10,68,101,102,105,110,105,116,105,111,110,115,32,109,97,121,32,98,101,32,97,116,32,109,111,115,116,32,50,48,32,99,104,97,114,97,99,116,101,114,115,33,10,94,62,118,60,0,1,0,-1,-1,0,1,0,0,0,0,0,0,1,14,0,0,109,4,1202,-3,1,587,20102,1,0,-1,22101,1,-3,-3,21102,0,1,-2,2208,-2,-1,570,1005,570,617,2201,-3,-2,609,4,0,21201,-2,1,-2,1105,1,597,109,-4,2105,1,0,109,5,1202,-4,1,630,20101,0,0,-2,22101,1,-4,-4,21102,0,1,-3,2208,-3,-2,570,1005,570,781,2201,-4,-3,652,21002,0,1,-1,1208,-1,-4,570,1005,570,709,1208,-1,-5,570,1005,570,734,1207,-1,0,570,1005,570,759,1206,-1,774,1001,578,562,684,1,0,576,576,1001,578,566,692,1,0,577,577,21101,0,702,0,1106,0,786,21201,-1,-1,-1,1105,1,676,1001,578,1,578,1008,578,4,570,1006,570,724,1001,578,-4,578,21101,0,731,0,1105,1,786,1105,1,774,1001,578,-1,578,1008,578,-1,570,1006,570,749,1001,578,4,578,21101,756,0,0,1106,0,786,1105,1,774,21202,-1,-11,1,22101,1182,1,1,21101,774,0,0,1106,0,622,21201,-3,1,-3,1105,1,640,109,-5,2106,0,0,109,7,1005,575,802,20101,0,576,-6,20101,0,577,-5,1106,0,814,21101,0,0,-1,21101,0,0,-5,21102,1,0,-6,20208,-6,576,-2,208,-5,577,570,22002,570,-2,-2,21202,-5,45,-3,22201,-6,-3,-3,22101,1441,-3,-3,2101,0,-3,843,1005,0,863,21202,-2,42,-4,22101,46,-4,-4,1206,-2,924,21102,1,1,-1,1105,1,924,1205,-2,873,21101,35,0,-4,1106,0,924,1201,-3,0,878,1008,0,1,570,1006,570,916,1001,374,1,374,1202,-3,1,895,1101,2,0,0,1201,-3,0,902,1001,438,0,438,2202,-6,-5,570,1,570,374,570,1,570,438,438,1001,578,558,922,20101,0,0,-4,1006,575,959,204,-4,22101,1,-6,-6,1208,-6,45,570,1006,570,814,104,10,22101,1,-5,-5,1208,-5,35,570,1006,570,810,104,10,1206,-1,974,99,1206,-1,974,1101,0,1,575,21101,973,0,0,1105,1,786,99,109,-7,2106,0,0,109,6,21102,0,1,-4,21102,1,0,-3,203,-2,22101,1,-3,-3,21208,-2,82,-1,1205,-1,1030,21208,-2,76,-1,1205,-1,1037,21207,-2,48,-1,1205,-1,1124,22107,57,-2,-1,1205,-1,1124,21201,-2,-48,-2,1105,1,1041,21102,-4,1,-2,1105,1,1041,21101,-5,0,-2,21201,-4,1,-4,21207,-4,11,-1,1206,-1,1138,2201,-5,-4,1059,1202,-2,1,0,203,-2,22101,1,-3,-3,21207,-2,48,-1,1205,-1,1107,22107,57,-2,-1,1205,-1,1107,21201,-2,-48,-2,2201,-5,-4,1090,20102,10,0,-1,22201,-2,-1,-2,2201,-5,-4,1103,2101,0,-2,0,1106,0,1060,21208,-2,10,-1,1205,-1,1162,21208,-2,44,-1,1206,-1,1131,1106,0,989,21102,439,1,1,1105,1,1150,21102,477,1,1,1106,0,1150,21101,514,0,1,21102,1149,1,0,1105,1,579,99,21101,1157,0,0,1105,1,579,204,-2,104,10,99,21207,-3,22,-1,1206,-1,1138,2101,0,-5,1176,2101,0,-4,0,109,-6,2106,0,0,10,5,40,1,44,1,44,1,44,7,44,1,44,1,7,13,24,1,7,1,11,1,8,7,9,1,7,1,11,1,8,1,5,1,9,1,7,1,11,1,8,1,5,1,9,1,1,5,1,1,5,9,6,1,5,1,9,1,1,1,3,1,1,1,5,1,5,1,1,1,6,1,5,1,7,11,1,11,1,1,6,1,5,1,7,1,1,1,1,1,3,1,3,1,3,1,7,1,6,1,5,1,7,1,1,7,3,1,3,1,7,1,6,1,5,1,7,1,3,1,7,1,3,1,7,1,6,1,5,1,1,11,1,11,7,1,6,1,5,1,1,1,5,1,5,1,5,1,11,1,6,1,5,9,5,1,5,1,11,1,6,1,7,1,11,1,5,1,11,1,6,7,1,1,11,1,5,7,5,7,6,1,1,1,11,1,11,1,11,1,6,1,1,13,11,1,11,1,6,1,25,1,11,1,6,1,25,1,11,1,6,1,25,1,11,1,6,1,25,1,11,1,6,1,25,1,11,1,6,1,25,1,1,11,6,1,25,1,1,1,16,7,19,7,40,1,3,1,40,1,3,1,40,1,3,1,40,5,6
""")