# this is pretty gross, but fuck it
class Memory(list):
    def __init__(self, size):
        self.data = {}
        self.size = size
        for i in range(0, size):
            self.append(0)

    def __getitem__(self, index):
        if index > self.size - 1:
            if index not in self.data:
                self.data[index] = 0
            return self.data[index]
        return super(list).__getitem__(index)

    def __setitem__(self, index, value):
        if index > self.size - 1:
            self.data[index] = value
        else:
            super(list).__setitem__(index, value)


class IntcodeComputerV2:
    def __init__(self,
                 input_string,
                 noun=None,
                 verb=None,
                 input_handler=None,
                 output_handler=None):
        self.instruction_pointer = 0

        parts = input_string.split(",")
        self.memory = {}
        for i, value in enumerate(parts):
            self.memory[i] = int(value)

        # self.memory = [int(i) for i in input_string.split(",")]
        self.halted = False
        self.output = 0

        if noun is not None:
            self.memory[1] = noun
        if verb is not None:
            self.memory[2] = verb

        self.input_handler = input_handler
        self.output_handler = output_handler

        self.relative_base = 0
        self.exit = False

    def run(self, input_values=[], return_on_output=False):
        instruction_pointer = self.instruction_pointer
        memory = self.memory
        relative_base = self.relative_base

        def getArguments(number_arguments):
            start = instruction_pointer + 1
            end = start + number_arguments
            args = []
            for i in range(start, end):
                args.append(memory[i])
            return args

        output = self.output

        while True and not self.exit:

            instruction = str(memory[instruction_pointer])
            instruction = instruction.rjust(5, '0')
            opCode = int(instruction[-2:])
            parts = [char for char in instruction]
            modes = [int(i) for i in parts[0:3]]
            modes.reverse()

            args = []

            def parseArg(index):
                argument = args[index]
                mode = modes[index]
                if mode == 0:
                    return memory[argument]
                elif mode == 1:
                    return argument
                elif mode == 2:
                    return memory[argument + relative_base]
                else:
                    raise Exception("Invalid mode: " + mode)

            if opCode == 1:
                # add
                args = getArguments(3)
                arg3 = args[2] + (relative_base if modes[2] == 2 else 0)
                memory[arg3] = parseArg(0) + parseArg(1)
                instruction_pointer += 4
            elif opCode == 2:
                # multiply
                args = getArguments(3)
                arg3 = args[2] + (relative_base if modes[2] == 2 else 0)
                memory[arg3] = parseArg(0) * parseArg(1)
                instruction_pointer += 4
            elif opCode == 3:
                # input
                if self.input_handler:
                    input_value = self.input_handler()
                else:
                    if input_values:
                        if instruction_pointer == 0 or len(input_values) < 2:
                            input_value = input_values[0]
                        else:
                            input_value = input_values[1]
                    else:
                        input_value = 0

                args = getArguments(1)
                arg0 = args[0] + (relative_base if modes[0] == 2 else 0)
                memory[arg0] = input_value
                instruction_pointer += 2
            elif opCode == 4:
                # output
                args = getArguments(1)
                output = parseArg(0)
                instruction_pointer += 2
                if self.output_handler:
                    self.output_handler(output, self)
                if return_on_output:
                    break
            elif opCode == 5:
                # jump if true
                args = getArguments(2)
                if parseArg(0):
                    instruction_pointer = parseArg(1)
                else:
                    instruction_pointer += 3
            elif opCode == 6:
                # jump if false
                args = getArguments(2)
                if not parseArg(0):
                    instruction_pointer = parseArg(1)
                else:
                    instruction_pointer += 3
            elif opCode == 7:
                # less than
                args = getArguments(3)
                arg3 = args[2] + (relative_base if modes[2] == 2 else 0)
                memory[arg3] = int(parseArg(0) < parseArg(1))
                instruction_pointer += 4
            elif opCode == 8:
                # equals
                args = getArguments(3)
                arg3 = args[2] + (relative_base if modes[2] == 2 else 0)
                memory[arg3] = int(parseArg(0) == parseArg(1))
                instruction_pointer += 4
            elif opCode == 9:
                # relative base
                args = getArguments(1)
                relative_base = relative_base + parseArg(0)
                instruction_pointer += 2
            elif opCode == 99:
                # halt
                instruction_pointer += 1
                self.halted = True
                break

        self.instruction_pointer = instruction_pointer
        self.relative_base = relative_base
        self.output = output

        return output