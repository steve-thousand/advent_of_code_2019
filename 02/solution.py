def solve(input):
    def initializeMemory(input):
        return map(lambda x: int(x), input.split(","))

    def run(memory):
        instruction_pointer = 0
        while instruction_pointer <= len(input):
            this = memory[instruction_pointer]
            if this == 1:
                sum = memory[memory[instruction_pointer +
                                    1]] + memory[memory[instruction_pointer +
                                                        2]]
                memory[memory[instruction_pointer + 3]] = sum
                instruction_pointer += 4
            elif this == 2:
                mul = memory[memory[instruction_pointer +
                                    1]] * memory[memory[instruction_pointer +
                                                        2]]
                memory[memory[instruction_pointer + 3]] = mul
                instruction_pointer += 4
            elif this == 99:
                break
            else:
                raise Exception("Oops")

    memory = initializeMemory(input)

    # part 1
    memory[1] = 12
    memory[2] = 2
    run(memory)
    print(memory[0])

    # part 2, i'm lazy so i'll just brute force it
    for noun in range(0, 99):
        for verb in range(0, 99):
            memory = initializeMemory(input)
            memory[1] = noun
            memory[2] = verb
            run(memory)
            if memory[0] == 19690720:
                print((100 * noun) + verb)


solve(
    "1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,6,19,1,9,19,23,2,23,10,27,1,27,5,31,1,31,6,35,1,6,35,39,2,39,13,43,1,9,43,47,2,9,47,51,1,51,6,55,2,55,10,59,1,59,5,63,2,10,63,67,2,9,67,71,1,71,5,75,2,10,75,79,1,79,6,83,2,10,83,87,1,5,87,91,2,9,91,95,1,95,5,99,1,99,2,103,1,103,13,0,99,2,14,0,0"
)
