import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from intcode import IntcodeComputer

from itertools import permutations

class Amplifier:
    def __init__(self, input_string, phase):
        self.intcode_computer = IntcodeComputer(input_string)
        self.phase = phase

    def run(self, input=0):
        return self.intcode_computer.run([self.phase, input])


def solve(input_string):

    def runAmplifiers(phase_setting, feedback_mode=False):
        '''Run the series of amplifiers with the provided phase setting'''
        # build amplifiers
        amplifiers = map(lambda i: Amplifier(input_string, i), phase_setting)

        last_output = 0
        while True:
            for amplifier in amplifiers:
                last_output = amplifier.run(last_output)
            if not feedback_mode:
                break
        return last_output

    def getMaxSignalForInput(input_string, feedback_mode=False):
        '''Print the max signal and phase setting for the provided input string'''
        max = 0
        max_phase = None

        if feedback_mode:
            perm = permutations([5, 6, 7, 8, 9])
        else:
            perm = permutations([0, 1, 2, 3, 4])

        for i in perm:
            output = runAmplifiers(i, feedback_mode)
            if output > max:
                max = output
                max_phase = i

        print(max)
        print(max_phase)

    # default
    # getMaxSignalForInput(input_string)

    # feedback
    getMaxSignalForInput("3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5", feedback_mode=True)

    return


solve(
    """3,8,1001,8,10,8,105,1,0,0,21,34,51,64,73,98,179,260,341,422,99999,3,9,102,4,9,9,1001,9,4,9,4,9,99,3,9,1001,9,4,9,1002,9,3,9,1001,9,5,9,4,9,99,3,9,101,5,9,9,102,5,9,9,4,9,99,3,9,101,5,9,9,4,9,99,3,9,1002,9,5,9,1001,9,3,9,102,2,9,9,101,5,9,9,1002,9,2,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,101,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,99"""
)
