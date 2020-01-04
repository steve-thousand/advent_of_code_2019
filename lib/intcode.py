from abc import ABC

class Operation(ABC):
    def __init__(self, arguments):
        self.arguments = arguments

    def execute(self, memory, instruction_pointer):
        '''Should return bool indicating if program should continue. False == stop'''
        pass

class Sum(Operation):
    def execute(self, m, i):
        m[m[i + 3]] = m[m[i + 1]] + m[m[i + 2]]
        return True

class Multiply(Operation):
    def execute(self, m, i):
        m[m[i + 3]] = m[m[i + 1]] * m[m[i + 2]]
        return True

class Break(Operation):
    def execute(self, m, i):
        return False

operations = {1: Sum(3), 2: Multiply(3), 99: Break(0)}

class IntcodeComputer:
    def __init__(self, input, noun, verb):
        self.memory = list(map(lambda x: int(x), input.split(",")))
        self.memory[1] = noun
        self.memory[2] = verb

    def run(self):
        memory = self.memory
        instruction_pointer = 0
        while instruction_pointer <= len(memory):
            operation = operations[memory[instruction_pointer]]
            if not operation.execute(memory, instruction_pointer):
                break
            instruction_pointer += 1 + operation.arguments

    def get(self, address):
        return self.memory[address]