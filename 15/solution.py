import sys, os, curses, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from intcode import IntcodeComputerV2 as IntcodeComputer

OBJECTS = {0: "#", 1: " ", 2: "O"}
MANUAL = False

DIRECTIONS = [
    curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_UP
]

# the order of turns that the bot will automatically take at any given point
TURNS = [
    1,  #RIGHT
    0,  #FORWARD
    3,  #LEFT
    2,  #BACK
]


def TURN(turn, direction):
    '''
    Calculate what new direction would be when performing the provided turn
    while facing the provided direction.
    '''
    current_direction_index = DIRECTIONS.index(direction)
    return DIRECTIONS[(current_direction_index + turn) % len(DIRECTIONS)]


def getPotentialPosition(current, key):
    if key == curses.KEY_RIGHT:
        return (current[0] + 1, current[1])
    elif key == curses.KEY_LEFT:
        return (current[0] - 1, current[1])
    elif key == curses.KEY_UP:
        return (current[0], current[1] - 1)
    elif key == curses.KEY_DOWN:
        return (current[0], current[1] + 1)
    raise Exception("Invalid input!")


def getAdjacentSpaces(current):
    adjacent = []
    for direction in DIRECTIONS:
        adjacent.append(getPotentialPosition(current, direction))
    return adjacent


class Game:
    def __init__(self, space):
        self.current = (0, 0)
        self.desired_position = (0, 0)
        self.oxygen_position = None
        self.space = space
        space[self.current] = 1
        self.unfinished_spaces = set()
        self.unfinished_spaces.add(self.current)
        return

    def attemptMove(self, key):
        current = self.current
        self.desired_position = getPotentialPosition(current, key)
        if key == curses.KEY_RIGHT:
            return 4
        elif key == curses.KEY_LEFT:
            return 3
        elif key == curses.KEY_UP:
            return 1
        elif key == curses.KEY_DOWN:
            return 2
        raise Exception("Invalid input!")

    def move(self):
        self.current = self.desired_position


class InputModule:
    def __init__(self, game, stdscr):
        self.game = game
        self.stdscr = stdscr
        stdscr.keypad(True)
        self.facing_direction = curses.KEY_RIGHT
        self.last_position = None
        return

    def __call__(self):
        if MANUAL:
            char = self.stdscr.getch()
            if char == 27: sys.exit()  # escape
            return self.game.attemptMove(char)
        else:
            return self.automatic()

    def automatic(self):
        '''
        Algorithm for moving through the maze. At every space:
        1. Try to move in this order (relative to the current trajectory):
            - RIGHT
            - FORWARD
            - LEFT
            - BACK
        2. After deciding to move, keep track of current position so that we can
        tell if we moved
        3.  a) if we did move, go back to step 1
            b) if we didn't move, we hit a wall. That direction won't work, turn left
        '''
        current = self.game.current
        space = self.game.space

        # time.sleep(.0001)

        def commitToDirection(potential_direction):
            self.facing_direction = potential_direction
            self.last_position = current
            return self.game.attemptMove(potential_direction)

        # are we exactly where we were last tick?
        if self.last_position and self.last_position == current:
            # the last decision to move was into a wall. current direction is wrong, turn left
            potential_direction = TURN(3, self.facing_direction)
            return commitToDirection(potential_direction)

        #let's try turning
        for turn in TURNS:
            potential_direction = TURN(turn, self.facing_direction)
            attempt = getPotentialPosition(current, potential_direction)
            if attempt not in space or space[attempt] != 0:
                return commitToDirection(potential_direction)


class OutputModule:
    def __init__(self, game, stdscr, width, height):
        self.game = game
        self.stdscr = stdscr
        curses.curs_set(0)
        self.width = width
        self.height = height
        return

    def __call__(self, output: int, intcodeComputer):
        space = self.game.space
        self.game.space[self.game.desired_position] = output
        if output == 1:
            self.game.move()
        if output == 2:
            self.game.move()
            self.game.oxygen_position = self.game.current

        # decide if there are spaces that need to be explored still
        found_unexplored = False
        for adjacent in getAdjacentSpaces(self.game.current):
            if adjacent not in space:
                self.game.unfinished_spaces.add(self.game.current)
                found_unexplored = True
                break
        if not found_unexplored and self.game.current in self.game.unfinished_spaces:
            self.game.unfinished_spaces.remove(self.game.current)

        # if there are not, exit
        if len(self.game.unfinished_spaces) == 0:
            intcodeComputer.exit = True

        # draw
        stdscr = self.stdscr
        stdscr.clear()

        half_height = self.height // 2
        half_width = self.width // 2

        current_x = self.game.current[0]
        current_y = self.game.current[1]

        for y in range(current_y - half_height, current_y + half_height):
            for x in range(current_x - half_width, current_x + half_width):
                this_x = x + half_width - current_x
                this_y = y + half_height - current_y
                if (x, y) in space:
                    stdscr.addstr(this_y, this_x, OBJECTS[space[(x, y)]])
                else:
                    stdscr.addstr(this_y, this_x, "▓")

        stdscr.addstr(half_height, half_width, "D")

        stdscr.refresh()

        return


def aStar(space, start, stop):
    queue = []
    queue.append((start, 0))
    visited = set()
    while len(queue) > 0:
        current = queue.pop()
        if current[0] == stop:
            return current[1]
        visited.add(current[0])
        # check all adjacent for open spaces
        for adjacent in getAdjacentSpaces(current[0]):
            if adjacent not in visited and adjacent in space and space[
                    adjacent] == 1:
                queue.append((adjacent, current[1] + 1))
        queue.sort(key=lambda x: x[1], reverse=True)
    raise Exception("FUCK!")


def breadthFirstTraverse(space, start):
    visited = set()
    frontier = [start]
    iterations = -1
    while len(frontier) > 0:
        iterations += 1
        next_frontier = []
        for cell in frontier:
            visited.add(cell)
            adjacent = getAdjacentSpaces(cell)
            for adjacent_cell in adjacent:
                if adjacent_cell not in visited and space[adjacent_cell] == 1:
                    next_frontier.append(adjacent_cell)
        frontier = next_frontier
    return iterations


def walkTheRegion(input_string, space):
    stdscr = curses.initscr()
    game = Game(space)
    intcodeComputer = IntcodeComputer(input_string,
                                      input_handler=InputModule(game, stdscr),
                                      output_handler=OutputModule(
                                          game, stdscr, 39, 13))
    intcodeComputer.run()
    curses.endwin()
    return game


def solve(input_string):
    space = {}
    game = walkTheRegion(input_string, space)
    print(aStar(space, game.oxygen_position, (0, 0)))
    print(breadthFirstTraverse(space, game.oxygen_position))
    return


solve(
    """3,1033,1008,1033,1,1032,1005,1032,31,1008,1033,2,1032,1005,1032,58,1008,1033,3,1032,1005,1032,81,1008,1033,4,1032,1005,1032,104,99,101,0,1034,1039,1001,1036,0,1041,1001,1035,-1,1040,1008,1038,0,1043,102,-1,1043,1032,1,1037,1032,1042,1105,1,124,101,0,1034,1039,101,0,1036,1041,1001,1035,1,1040,1008,1038,0,1043,1,1037,1038,1042,1106,0,124,1001,1034,-1,1039,1008,1036,0,1041,1001,1035,0,1040,1001,1038,0,1043,1002,1037,1,1042,1105,1,124,1001,1034,1,1039,1008,1036,0,1041,102,1,1035,1040,101,0,1038,1043,1002,1037,1,1042,1006,1039,217,1006,1040,217,1008,1039,40,1032,1005,1032,217,1008,1040,40,1032,1005,1032,217,1008,1039,1,1032,1006,1032,165,1008,1040,33,1032,1006,1032,165,1101,0,2,1044,1106,0,224,2,1041,1043,1032,1006,1032,179,1101,1,0,1044,1106,0,224,1,1041,1043,1032,1006,1032,217,1,1042,1043,1032,1001,1032,-1,1032,1002,1032,39,1032,1,1032,1039,1032,101,-1,1032,1032,101,252,1032,211,1007,0,43,1044,1105,1,224,1101,0,0,1044,1106,0,224,1006,1044,247,1002,1039,1,1034,1002,1040,1,1035,102,1,1041,1036,1001,1043,0,1038,101,0,1042,1037,4,1044,1105,1,0,13,30,60,64,5,28,36,24,67,12,1,67,32,39,14,78,29,17,38,88,79,9,62,25,15,18,88,25,7,81,38,41,10,69,86,32,11,33,1,10,22,84,14,92,48,79,10,3,62,33,61,13,93,78,20,63,68,17,80,34,12,8,23,61,90,51,17,84,37,46,64,25,3,73,19,45,99,41,62,21,77,8,17,89,9,13,84,75,85,14,53,60,6,29,76,63,14,23,63,61,93,72,17,41,28,94,5,3,19,47,57,55,14,34,38,79,85,40,13,22,99,67,72,15,62,15,6,63,3,90,2,87,20,84,15,50,70,27,18,78,21,70,48,52,2,99,92,55,3,46,41,93,99,88,13,39,4,45,71,3,96,1,91,59,31,53,23,25,82,32,50,16,60,38,78,34,59,30,15,51,92,3,22,26,62,60,37,42,74,28,21,76,7,24,70,18,40,11,81,41,9,73,62,12,66,81,9,3,74,62,11,6,56,16,34,20,78,79,1,97,17,39,87,15,12,77,94,28,22,66,45,59,39,2,6,52,6,72,49,17,92,15,86,18,92,79,67,20,22,72,10,72,3,52,26,77,78,41,97,36,59,88,24,57,12,38,90,53,14,38,67,2,36,44,93,99,10,41,49,3,16,7,63,32,11,15,81,12,91,39,62,19,83,6,91,28,19,80,38,23,63,31,71,14,58,8,21,71,21,21,81,38,26,32,29,82,52,28,72,54,97,41,65,96,75,1,48,28,80,66,25,47,49,29,87,51,12,50,70,36,60,81,29,77,76,55,25,40,45,83,91,26,72,99,12,47,11,20,27,52,9,98,17,99,27,37,62,25,3,15,73,66,22,5,85,5,20,98,20,38,62,78,21,16,59,28,98,38,31,2,40,46,87,14,48,33,80,48,36,27,56,21,1,50,83,3,61,92,20,52,16,50,10,86,9,98,39,56,25,50,42,39,91,81,56,25,70,44,24,15,99,4,20,55,12,98,27,65,20,77,97,76,36,42,87,6,11,79,65,16,65,44,13,90,13,48,79,13,95,60,19,55,24,66,4,53,11,23,68,14,97,53,45,14,16,93,18,29,83,5,6,77,19,70,97,34,20,70,52,11,74,14,72,10,36,44,33,45,19,38,36,77,5,37,51,1,55,17,2,48,23,18,2,34,90,97,24,30,51,66,33,70,51,37,31,51,37,65,55,18,8,66,4,65,62,26,93,29,88,3,75,73,24,23,67,1,13,68,7,36,87,62,48,1,31,45,28,62,86,24,98,1,59,49,37,26,62,36,44,66,18,17,97,92,40,36,65,80,84,5,84,6,79,87,36,31,96,15,71,96,2,72,11,81,95,94,41,54,31,58,25,74,24,51,81,38,32,73,22,96,40,62,22,59,74,39,25,86,2,55,20,61,40,37,88,69,1,60,42,18,31,54,13,27,19,93,34,41,99,33,89,20,16,52,84,32,94,31,6,61,25,1,61,1,38,78,87,39,31,39,26,68,42,36,2,94,66,2,67,30,80,2,95,65,40,54,50,33,11,23,97,89,1,31,56,9,35,49,92,55,23,84,48,91,20,7,72,25,55,3,85,3,16,40,90,22,99,44,38,86,98,11,76,26,76,13,82,80,24,93,4,15,64,95,58,15,85,25,57,29,66,3,66,19,98,57,24,44,59,35,76,48,31,92,33,94,68,56,41,45,15,46,5,68,15,65,34,73,49,68,17,78,28,80,24,59,26,74,21,52,1,94,5,61,41,88,37,56,1,49,0,0,21,21,1,10,1,0,0,0,0,0,0"""
)
