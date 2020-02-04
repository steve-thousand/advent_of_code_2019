import re, sys, ujson

pattern = re.compile(r"<x=(-?\d+), y=(-?\d+), z=(-?\d+)>")


def solve(steps, input_string):

    # yeah
    TOTAL_MOONS = 4

    def parse_moons(input_string):
        moons = []
        for i in input_string.split("\n"):
            match = pattern.match(i)
            x = int(match.group(1))
            y = int(match.group(2))
            z = int(match.group(3))
            moons.append([x, y, z, 0, 0, 0])
        return moons

    def simulate(moons, goal_steps=steps, find_steps_to_previous_state=False):

        states = set()
        steps = 0

        while steps != goal_steps:

            # persist state
            moon_string = ujson.dumps(moons)
            if moon_string in states and find_steps_to_previous_state:
                return steps
            states.add(moon_string)

            def sign(number):
                if number != 0:
                    # trying to calculate sign without using conditionals
                    return (number >> 31) - (-number >> 31)
                return 0

            for i in range(TOTAL_MOONS):
                moon = moons[i]
                for j in range(i + 1, TOTAL_MOONS):
                    other_moon = moons[j]
                    diff_sign = sign(other_moon[0] - moon[0])
                    moon[3] += diff_sign
                    other_moon[3] -= diff_sign

                    diff_sign = sign(other_moon[1] - moon[1])
                    moon[4] += diff_sign
                    other_moon[4] -= diff_sign

                    diff_sign = sign(other_moon[2] - moon[2])
                    moon[5] += diff_sign
                    other_moon[5] -= diff_sign

                moon[0] += moon[3]
                moon[1] += moon[4]
                moon[2] += moon[5]

            steps += 1
            if steps % 10000 == 0:
                print(steps)

    def getTotalEnergy(moons):
        total_energy = 0
        for moon in moons:
            potential = abs(moon[0]) + abs(moon[1]) + abs(moon[2])
            kinetic = abs(moon[3]) + abs(moon[4]) + abs(moon[5])
            total_energy += potential * kinetic
        return total_energy

    # get total energy after 1000 steps
    moons = parse_moons(input_string)
    simulate(moons)
    print(getTotalEnergy(moons))

    # find how many steps until we get to a previous state
    moons = parse_moons(input_string)
    print(
        simulate(moons,
                 goal_steps=sys.maxsize,
                 find_steps_to_previous_state=True))


solve(
    1000, """<x=16, y=-8, z=13>
<x=4, y=10, z=10>
<x=17, y=-5, z=6>
<x=13, y=-3, z=0>""")