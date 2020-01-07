import sys, os, unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from intcode import IntcodeComputer, Operation, Sum, Multiply, LessThan, Equals, OpParams


class Test(unittest.TestCase):
    def test(self):
        op = Operation.parseOp("1002")
        self.assertEqual([0, 1, 0], op.op_params.modes)


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
            intcodeComputer = IntcodeComputer(i[0])
            intcodeComputer.run([1])
            self.assertEqual(i[1], intcodeComputer.memory)

    def testOuput(self):
        intcodeComputer = IntcodeComputer("3,0,4,4,99")
        output = intcodeComputer.run([1])
        self.assertEqual(99, output)

    def testJump(self):
        # position mode
        intcodeComputer = IntcodeComputer(
            "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9")
        self.assertEqual(1, intcodeComputer.run([-1]))
        intcodeComputer = IntcodeComputer(
            "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9")
        self.assertEqual(0, intcodeComputer.run([0]))
        intcodeComputer = IntcodeComputer(
            "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9")
        self.assertEqual(1, intcodeComputer.run([1]))

        # immediate mode
        intcodeComputer = IntcodeComputer(
            "3,3,1105,-1,9,1101,0,0,12,4,12,99,1")
        self.assertEqual(1, intcodeComputer.run([-1]))
        intcodeComputer = IntcodeComputer(
            "3,3,1105,-1,9,1101,0,0,12,4,12,99,1")
        self.assertEqual(0, intcodeComputer.run([0]))
        intcodeComputer = IntcodeComputer(
            "3,3,1105,-1,9,1101,0,0,12,4,12,99,1")
        self.assertEqual(1, intcodeComputer.run([1]))


class SumOperationTests(unittest.TestCase):
    def testWithPositionMode(self):
        op = Sum(OpParams([0, 0, 0]))
        memory = [2, 4, 5, 3, 1, 2]
        op.execute(memory, 0)
        self.assertEqual([2, 4, 5, 3, 1, 2], memory)

    def testWithImmediateMode(self):
        op = Sum(OpParams([1, 1, 0]))
        memory = [2, 4, 5, 3, 5, 6]
        op.execute(memory, 0)
        self.assertEqual([2, 4, 5, 9, 5, 6], memory)


class MultiplyOperationTests(unittest.TestCase):
    def testWithPositionMode(self):
        op = Multiply(OpParams([0, 0, 0]))
        memory = [2, 4, 5, 3, 1, 2]
        op.execute(memory, 0)
        self.assertEqual([2, 4, 5, 2, 1, 2], memory)

    def testWithImmediateMode(self):
        op = Multiply(OpParams([1, 1, 0]))
        memory = [2, 4, 5, 3, 5, 6]
        op.execute(memory, 0)
        self.assertEqual([2, 4, 5, 20, 5, 6], memory)


class LessThanOperationTests(unittest.TestCase):
    def test(self):
        # position mode
        intcodeComputer = IntcodeComputer("3,9,7,9,10,9,4,9,99,-1,8")
        self.assertEqual(1, intcodeComputer.run([7]))
        intcodeComputer = IntcodeComputer("3,9,7,9,10,9,4,9,99,-1,8")
        self.assertEqual(0, intcodeComputer.run([8]))
        intcodeComputer = IntcodeComputer("3,9,7,9,10,9,4,9,99,-1,8")
        self.assertEqual(0, intcodeComputer.run([9]))

        # immediate mode
        intcodeComputer = IntcodeComputer("3,3,1107,-1,8,3,4,3,99")
        self.assertEqual(1, intcodeComputer.run([7]))
        intcodeComputer = IntcodeComputer("3,3,1107,-1,8,3,4,3,99")
        self.assertEqual(0, intcodeComputer.run([8]))
        intcodeComputer = IntcodeComputer("3,3,1107,-1,8,3,4,3,99")
        self.assertEqual(0, intcodeComputer.run([9]))


class EqualsOperationTests(unittest.TestCase):
    def test(self):
        # position mode
        intcodeComputer = IntcodeComputer("3,9,8,9,10,9,4,9,99,-1,8")
        self.assertEqual(0, intcodeComputer.run([7]))
        intcodeComputer = IntcodeComputer("3,9,8,9,10,9,4,9,99,-1,8")
        self.assertEqual(1, intcodeComputer.run([8]))
        intcodeComputer = IntcodeComputer("3,9,8,9,10,9,4,9,99,-1,8")
        self.assertEqual(0, intcodeComputer.run([9]))

        # immediate mode
        intcodeComputer = IntcodeComputer("3,3,1108,-1,8,3,4,3,99")
        self.assertEqual(0, intcodeComputer.run([7]))
        intcodeComputer = IntcodeComputer("3,3,1108,-1,8,3,4,3,99")
        self.assertEqual(1, intcodeComputer.run([8]))
        intcodeComputer = IntcodeComputer("3,3,1108,-1,8,3,4,3,99")
        self.assertEqual(0, intcodeComputer.run([9]))


unittest.main()