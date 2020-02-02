import cProfile, numpy
from re import sub

BASE_PATTERN = [0, 1, 0, -1]


def fftByOffset(input_array, phases, offset):
    sub_array = input_array[offset:]
    for phase_number in range(0, phases):

        print("Phasing... {}%".format(int((phase_number / phases) * 100)),
              end="\r")
        '''
        THIS IS A HACK
        At this point, the numbers should be so large, that the patterns can pretty much
        be assumed to be 1.
        '''
        '''Also, wow, calculating dynamically by summing in reverse is great'''
        memo = {}

        output_array = [0] * len(sub_array)
        for i in range(1, len(sub_array) + 1):
            if i - 1 in memo:
                total = memo[i - 1] + sub_array[-i]
            else:
                total = sum(sub_array[-i:])
            memo[i] = total
            output_array[-i] = abs(total) % 10
        sub_array = output_array

    print("Done phasing!")

    return sub_array


def solve(puzzle_input):
    def generatePattern(number, length, offset=0):
        '''
        generatePattern(1,8) == [ 1, 0,-1, 0,1 , 0,-1, 0]
        generatePattern(2,8) == [ 0, 1, 1, 0, 0,-1,-1, 0]
        generatePattern(3,8) == [ 0, 0, 1, 1, 1, 0, 0, 0]
        '''
        pattern = [0] * (length - offset)
        base_pattern_index = 0
        index = -1

        len_of_base_pattern = len(BASE_PATTERN)

        while index < length:
            for i in range(0, number):
                if index < offset or (index < 0 and i == 0):
                    index += 1
                    continue
                if index == length:
                    break
                pattern[index - offset] = BASE_PATTERN[base_pattern_index %
                                                       len_of_base_pattern]
                index += 1
            base_pattern_index += 1
        return numpy.array(pattern)

    def generatePatterns(length):
        patterns = [None] * length
        for i in range(0, length):
            patterns[i] = generatePattern(i + 1, length)
        return numpy.array(patterns)

    def phase(input_array, patterns):
        '''Matrix multiplication (numpy proved to be VERY fast)'''
        numpy.matmul(patterns, input_array, out=input_array)
        for i, number in enumerate(input_array):
            input_array[i] = abs(number) % 10

    def fft(input_array, phases=1):
        length = len(input_array)
        input_array = numpy.array(input_array)
        patterns = generatePatterns(length)
        for phase_number in range(0, phases):
            phase(input_array, patterns)
        return input_array

    # part 1
    output_array = fft([int(char) for char in puzzle_input], 100)
    print(''.join(str(number) for number in output_array[:8]))

    # part 2
    offset = int(puzzle_input[:7])
    output_array = fftByOffset([int(char) for char in puzzle_input] * 10000,
                               100, offset)
    print(''.join(str(number) for number in output_array[:8]))

    return


solve(
    """59704176224151213770484189932636989396016853707543672704688031159981571127975101449262562108536062222616286393177775420275833561490214618092338108958319534766917790598728831388012618201701341130599267905059417956666371111749252733037090364984971914108277005170417001289652084308389839318318592713462923155468396822247189750655575623017333088246364350280299985979331660143758996484413769438651303748536351772868104792161361952505811489060546839032499706132682563962136170941039904873411038529684473891392104152677551989278815089949043159200373061921992851799948057507078358356630228490883482290389217471790233756775862302710944760078623023456856105493"""
)
