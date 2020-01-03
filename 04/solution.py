def validPassword(password):
    prev = -1
    adjacentTotal = 0
    foundOnly2Adjacent = False
    if len(password) != 6:
        return False
    for i in range(0, len(password)):
        digit = int(password[i])
        if prev == -1:
            prev = digit
        else:
            if digit < prev:
                # not ascending
                return False
            if digit == prev:
                adjacentTotal += 1

            #GROSS
            if prev != digit or i == len(password) - 1:
                if adjacentTotal == 1:
                    foundOnly2Adjacent = True
                adjacentTotal = 0
            prev = digit

    return foundOnly2Adjacent


def solve(input):

    total = 0

    ends = input.split("-")

    for i in range(int(ends[0]), int(ends[1])):
        if validPassword(str(i)) is True:
            total += 1
            # print(i)

    print(total)


# print(validPassword("222333"))
solve("183564-657474")