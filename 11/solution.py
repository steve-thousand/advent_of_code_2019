import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from intcode import IntcodeComputerV2 as IntcodeComputer

from enum import Enum


class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


def paint(space, input_string, starting_white=False):
    panels_painted = 0
    x = 0
    y = 0
    direction = Direction.UP

    intcodeComputer = IntcodeComputer(input_string)

    while (True):
        if (x, y) not in space:
            space[(x, y)] = starting_white
            panels_painted += 1
        current_color = int(space[(x, y)])

        white = bool(
            intcodeComputer.run([current_color], return_on_output=True))
        right = bool(
            intcodeComputer.run([current_color], return_on_output=True))

        space[(x, y)] = white

        # decide where to go next
        if direction == Direction.UP:
            direction = Direction.RIGHT if right else Direction.LEFT
        elif direction == Direction.RIGHT:
            direction = Direction.DOWN if right else Direction.UP
        elif direction == Direction.DOWN:
            direction = Direction.LEFT if right else Direction.RIGHT
        elif direction == Direction.LEFT:
            direction = Direction.UP if right else Direction.DOWN

        if direction == Direction.UP:
            y -= 1
        elif direction == Direction.RIGHT:
            x += 1
        elif direction == Direction.DOWN:
            y += 1
        elif direction == Direction.LEFT:
            x -= 1

        if intcodeComputer.halted:
            break


def solve(input_string):

    # first part, starting from 0
    space = {}
    paint(space, input_string)
    print(len(space))

    # sercond part, starting from 1
    space = {}
    paint(space, input_string, starting_white=True)

    # translate space dictionary to 2d array

    ## get our x/y offset
    min_x = sys.maxsize
    max_x = -sys.maxsize
    min_y = sys.maxsize
    max_y = -sys.maxsize
    for key in space:
        if key[0] < min_x:
            min_x = key[0]
        if key[0] > max_x:
            max_x = key[0]
        if key[1] < min_y:
            min_y = key[1]
        if key[1] > max_y:
            max_y = key[1]

    ## build large enough 2d array
    array = [[False for i in range(abs(max_x - min_x + 1))]
             for j in range(abs(max_y - min_y + 1))]

    ## populate array
    for key in space:
        if space[key]:
            try:
                array[key[1] - min_y][key[0] - min_x] = True
            except IndexError:
                raise

    ## print
    print('\n'.join(''.join(("▓" if value else " ") for value in row)
                    for row in array))

    return


solve(
    """3,8,1005,8,325,1106,0,11,0,0,0,104,1,104,0,3,8,102,-1,8,10,1001,10,1,10,4,10,108,0,8,10,4,10,101,0,8,28,2,3,7,10,2,1109,3,10,2,102,0,10,2,1005,12,10,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,0,10,4,10,101,0,8,67,2,109,12,10,1,1003,15,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,108,1,8,10,4,10,101,0,8,96,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,0,10,4,10,1002,8,1,119,3,8,102,-1,8,10,1001,10,1,10,4,10,1008,8,0,10,4,10,101,0,8,141,3,8,1002,8,-1,10,101,1,10,10,4,10,108,0,8,10,4,10,1001,8,0,162,1,106,17,10,1006,0,52,1006,0,73,3,8,102,-1,8,10,1001,10,1,10,4,10,108,1,8,10,4,10,1001,8,0,194,1006,0,97,1,1004,6,10,1006,0,32,2,8,20,10,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,1,10,4,10,102,1,8,231,1,1,15,10,1006,0,21,1,6,17,10,2,1005,8,10,3,8,102,-1,8,10,101,1,10,10,4,10,108,1,8,10,4,10,102,1,8,267,2,1007,10,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,1,10,4,10,102,1,8,294,1006,0,74,2,1003,2,10,1,107,1,10,101,1,9,9,1007,9,1042,10,1005,10,15,99,109,647,104,0,104,1,21101,936333018008,0,1,21101,342,0,0,1106,0,446,21102,937121129228,1,1,21101,0,353,0,1105,1,446,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,21101,0,209383001255,1,21102,400,1,0,1106,0,446,21101,0,28994371675,1,21101,411,0,0,1105,1,446,3,10,104,0,104,0,3,10,104,0,104,0,21101,867961824000,0,1,21101,0,434,0,1106,0,446,21102,1,983925674344,1,21101,0,445,0,1106,0,446,99,109,2,21201,-1,0,1,21102,40,1,2,21101,477,0,3,21102,467,1,0,1106,0,510,109,-2,2106,0,0,0,1,0,0,1,109,2,3,10,204,-1,1001,472,473,488,4,0,1001,472,1,472,108,4,472,10,1006,10,504,1101,0,0,472,109,-2,2106,0,0,0,109,4,1201,-1,0,509,1207,-3,0,10,1006,10,527,21102,1,0,-3,21202,-3,1,1,21201,-2,0,2,21102,1,1,3,21102,1,546,0,1106,0,551,109,-4,2105,1,0,109,5,1207,-3,1,10,1006,10,574,2207,-4,-2,10,1006,10,574,22101,0,-4,-4,1105,1,642,21202,-4,1,1,21201,-3,-1,2,21202,-2,2,3,21101,0,593,0,1105,1,551,22102,1,1,-4,21101,1,0,-1,2207,-4,-2,10,1006,10,612,21102,1,0,-1,22202,-2,-1,-2,2107,0,-3,10,1006,10,634,21201,-1,0,1,21101,634,0,0,105,1,509,21202,-2,-1,-2,22201,-4,-2,-4,109,-5,2106,0,0"""
)
