from abc import ABC


class OperationResult:
    def __init__(self, should_continue, instruction_pointer, output=None):
        self.should_continue = should_continue
        self.instruction_pointer = instruction_pointer
        self.output = output


class Operation(ABC):
    def __init__(self, op_params):
        self.op_params = op_params

    def execute(self, memory, instruction_pointer):
        '''Should return OperationResult'''
        pass

    def get(self, memory, argument, mode):
        '''Retrieve from memory given an argument and an argument mode'''
        if self.op_params.modes[mode] == 1:
            return memory[argument]
        elif self.op_params.modes[mode] == 0:
            return memory[memory[argument]]
        else:
            raise Exception("Invalid mode: " + str(mode))

    @staticmethod
    def parseOp(op, input=None):
        opCode = int(op[-2:])
        modes = [0, 0, 0]
        if len(op) > 2:
            modes_string = op[:-2]
            modes_string = modes_string.rjust(3, '0')
            modes = [
                int(modes_string[2]),
                int(modes_string[1]),
                int(modes_string[0])
            ]
        return operations[opCode](OpParams(modes, input))


class Sum(Operation):
    def execute(self, m, i):
        # resolve first argument
        first_value = self.get(m, i + 1, 0)

        # resolve second argument
        second_value = self.get(m, i + 2, 1)

        # write to third argument
        m[m[i + 3]] = first_value + second_value

        return OperationResult(True, i + 4)


class Multiply(Operation):
    def execute(self, m, i):
        # resolve first argument
        first_value = self.get(m, i + 1, 0)

        # resolve second argument
        second_value = self.get(m, i + 2, 1)

        # write to third argument
        m[m[i + 3]] = first_value * second_value

        return OperationResult(True, i + 4)


class Break(Operation):
    def execute(self, m, i):
        return OperationResult(False, i)


class Input(Operation):
    def execute(self, m, i):
        m[m[i + 1]] = self.op_params.input.pop(0)
        return OperationResult(True, i + 2)


class Output(Operation):
    def execute(self, m, i):
        output = m[m[i + 1]]
        return OperationResult(True, i + 2, output=output)


class JumpIfTrue(Operation):
    def execute(self, m, i):
        value = self.get(m, i + 1, 0)
        jump_to = self.get(m, i + 2, 1)
        return OperationResult(True, jump_to if value else i + 3)


class JumpIfFalse(Operation):
    def execute(self, m, i):
        value = self.get(m, i + 1, 0)
        jump_to = self.get(m, i + 2, 1)
        return OperationResult(True, jump_to if not value else i + 3)


class LessThan(Operation):
    def execute(self, m, i):
        # resolve first argument
        first_value = self.get(m, i + 1, 0)

        # resolve second argument
        second_value = self.get(m, i + 2, 1)

        # write to third argument
        m[m[i + 3]] = 1 if first_value < second_value else 0

        return OperationResult(True, i + 4)


class Equals(Operation):
    def execute(self, m, i):
        # resolve first argument
        first_value = self.get(m, i + 1, 0)

        # resolve second argument
        second_value = self.get(m, i + 2, 1)

        # write to third argument
        m[m[i + 3]] = 1 if first_value == second_value else 0

        return OperationResult(True, i + 4)


class OpParams:
    def __init__(self, modes, input=None):
        self.modes = modes
        self.input = input


operations = {
    1: lambda params: Sum(params),
    2: lambda params: Multiply(params),
    3: lambda params: Input(params),
    4: lambda params: Output(params),
    5: lambda params: JumpIfTrue(params),
    6: lambda params: JumpIfFalse(params),
    7: lambda params: LessThan(params),
    8: lambda params: Equals(params),
    99: lambda params: Break(params)
}


class IntcodeComputer:
    def __init__(self, source, noun=None, verb=None, input=[]):
        self.memory = list(map(lambda x: int(x), source.split(",")))
        if noun:
            self.memory[1] = noun
        if verb:
            self.memory[2] = verb

        if isinstance(input, int):
            input = [input]
        self.input = input

    def run(self):
        memory = self.memory
        instruction_pointer = 0
        output = None
        while instruction_pointer <= len(memory):
            operation = Operation.parseOp(str(memory[instruction_pointer]),
                                          self.input)
            result = operation.execute(memory, instruction_pointer)
            if result.output is not None:
                output = result.output
            if not result.should_continue:
                break
            instruction_pointer = result.instruction_pointer

        return output

    def get(self, address):
        return self.memory[address]