import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from intcode import IntcodeComputer

from itertools import permutations


def solve(input_string):
    def runAmplifier(input1, input2):
        intcodeComputer = IntcodeComputer(input_string, input=[input1, input2])
        return intcodeComputer.run()

    def run(phase_setting):
        last = 0
        for i in phase_setting:
            last = runAmplifier(i, last)
        return last

    max = 0
    max_phase = None
    perm = permutations([0, 1, 2, 3, 4])
    for i in perm:
        output = run(i)
        if output > max:
            max = output
            max_phase = i

    print(max)
    print(max_phase)

    # feedback mode
    perm = permutations([5, 6, 7, 8, 9])

    return


solve(
    """3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5"""
)
