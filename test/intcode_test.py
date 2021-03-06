import sys, os, unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from intcode import IntcodeComputerV2


class IntcodeComputerTests(unittest.TestCase):

    testCases = [["1,0,0,0,99", [2, 0, 0, 0, 99]],
                 ["2,3,0,3,99", [2, 3, 0, 6, 99]],
                 ["2,4,4,5,99,0", [2, 4, 4, 5, 99, 9801]],
                 ["1,1,1,4,99,5,6,0,99", [30, 1, 1, 4, 2, 5, 6, 0, 99]],
                 [
                     "1,9,10,3,2,3,11,0,99,30,40,50",
                     [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50]
                 ], ["1002,4,3,4,33", [1002, 4, 3, 4, 99]],
                 ["1101,100,-1,4,0", [1101, 100, -1, 4, 99]],
                 ["3,0,99", [1, 0, 99]], ["3,0,4,4,99", [1, 0, 4, 4, 99]]]

    def test(self):
        for i in self.testCases:
            intcodeComputer = IntcodeComputerV2(i[0])
            intcodeComputer.run([1])
            self.assertEqual(i[1], intcodeComputer.memory)

    def testOuput(self):
        intcodeComputer = IntcodeComputerV2("3,0,4,4,99")
        output = intcodeComputer.run([1])
        self.assertEqual(99, output)

    def testJump(self):
        # position mode
        intcodeComputer = IntcodeComputerV2(
            "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9")
        self.assertEqual(1, intcodeComputer.run([-1]))
        intcodeComputer = IntcodeComputerV2(
            "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9")
        self.assertEqual(0, intcodeComputer.run([0]))
        intcodeComputer = IntcodeComputerV2(
            "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9")
        self.assertEqual(1, intcodeComputer.run([1]))

        # immediate mode
        intcodeComputer = IntcodeComputerV2(
            "3,3,1105,-1,9,1101,0,0,12,4,12,99,1")
        self.assertEqual(1, intcodeComputer.run([-1]))
        intcodeComputer = IntcodeComputerV2(
            "3,3,1105,-1,9,1101,0,0,12,4,12,99,1")
        self.assertEqual(0, intcodeComputer.run([0]))
        intcodeComputer = IntcodeComputerV2(
            "3,3,1105,-1,9,1101,0,0,12,4,12,99,1")
        self.assertEqual(1, intcodeComputer.run([1]))


class LessThanOperationTests(unittest.TestCase):
    def test(self):
        # position mode
        intcodeComputer = IntcodeComputerV2("3,9,7,9,10,9,4,9,99,-1,8")
        self.assertEqual(1, intcodeComputer.run([7]))
        intcodeComputer = IntcodeComputerV2("3,9,7,9,10,9,4,9,99,-1,8")
        self.assertEqual(0, intcodeComputer.run([8]))
        intcodeComputer = IntcodeComputerV2("3,9,7,9,10,9,4,9,99,-1,8")
        self.assertEqual(0, intcodeComputer.run([9]))

        # immediate mode
        intcodeComputer = IntcodeComputerV2("3,3,1107,-1,8,3,4,3,99")
        self.assertEqual(1, intcodeComputer.run([7]))
        intcodeComputer = IntcodeComputerV2("3,3,1107,-1,8,3,4,3,99")
        self.assertEqual(0, intcodeComputer.run([8]))
        intcodeComputer = IntcodeComputerV2("3,3,1107,-1,8,3,4,3,99")
        self.assertEqual(0, intcodeComputer.run([9]))


class EqualsOperationTests(unittest.TestCase):
    def test(self):
        # position mode
        intcodeComputer = IntcodeComputerV2("3,9,8,9,10,9,4,9,99,-1,8")
        self.assertEqual(0, intcodeComputer.run([7]))
        intcodeComputer = IntcodeComputerV2("3,9,8,9,10,9,4,9,99,-1,8")
        self.assertEqual(1, intcodeComputer.run([8]))
        intcodeComputer = IntcodeComputerV2("3,9,8,9,10,9,4,9,99,-1,8")
        self.assertEqual(0, intcodeComputer.run([9]))

        # immediate mode
        intcodeComputer = IntcodeComputerV2("3,3,1108,-1,8,3,4,3,99")
        self.assertEqual(0, intcodeComputer.run([7]))
        intcodeComputer = IntcodeComputerV2("3,3,1108,-1,8,3,4,3,99")
        self.assertEqual(1, intcodeComputer.run([8]))
        intcodeComputer = IntcodeComputerV2("3,3,1108,-1,8,3,4,3,99")
        self.assertEqual(0, intcodeComputer.run([9]))


unittest.main()