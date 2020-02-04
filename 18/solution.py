from typing import Tuple, List, Dict, Any, Set
from itertools import permutations
import sys

Cell = Tuple[int, int]  # (x, y)
PathInfo = Tuple[
    List[Cell], Set[str],
    Set[str]]  # ([cells in path], set(keys passed), set(doors passed))


def isDoor(char):
    # uppercase == door
    return ord(char) >= 65 and ord(char) < 91


def isKey(char):
    # lowercase == key
    return ord(char) >= 97 and ord(char) < 123


def parseRegion(puzzle_input, start, stop, overrides):
    keys = {}
    current_location = None
    for y, row in enumerate(puzzle_input.split("\n")):
        if y >= start[1] and y <= stop[1]:
            for x, char in enumerate(row):
                if x >= start[0] and x <= stop[0]:

                    # check to see if overrides specifies a char for this location
                    if (x, y) in overrides:
                        char = overrides[(x, y)]

                    if char == "@":
                        current_location = (x, y)
                    if isKey(char):
                        keys[char] = (x, y)
    return {"keys": keys, "current_location": current_location}


def parsePuzzleInput(puzzle_input, part2=False):
    space = {}
    doors = {}

    entrance_location = (-1, -1)

    max_x = 0
    max_y = 0
    for y, row in enumerate(puzzle_input.split("\n")):
        if y > max_y:
            max_y = y
        for x, char in enumerate(row):
            if x > max_x:
                max_x = x
            if char != "#":
                space[(x, y)] = char
            if char == "@":
                entrance_location = (x, y)
            if isDoor(char):
                doors[char] = (x, y)

    regions = []
    if part2:
        '''LUCKILY in my output we can just divied the space into quarters'''
        # remove spaces at, and adjacent to entrance_location
        del space[entrance_location]
        adjacent_cells = findAdjacentCells(space, entrance_location)
        for adjacent_cell in adjacent_cells:
            del space[adjacent_cell]

        # define where 4 entrances are
        new_entrance = (entrance_location[0] - 1, entrance_location[1] - 1)
        overrides = {new_entrance: "@"}
        regions.append(
            parseRegion(puzzle_input, (0, 0), new_entrance, overrides))

        new_entrance = (entrance_location[0] + 1, entrance_location[1] - 1)
        overrides = {new_entrance: "@"}
        regions.append(
            parseRegion(puzzle_input, (new_entrance[0], 0),
                        (max_x, new_entrance[1]), overrides))

        new_entrance = (entrance_location[0] - 1, entrance_location[1] + 1)
        overrides = {new_entrance: "@"}
        regions.append(
            parseRegion(puzzle_input, (0, new_entrance[1]),
                        (new_entrance[0], max_y), overrides))

        new_entrance = (entrance_location[0] + 1, entrance_location[1] + 1)
        overrides = {new_entrance: "@"}
        regions.append(
            parseRegion(puzzle_input, new_entrance, (max_x, max_y), overrides))
    else:
        region = parseRegion(puzzle_input, (0, 0), (max_x, max_y), {})
        regions.append(region)

    return {
        "space": space,
        "regions": regions,
        "found_keys": set(),
        "doors": doors
    }


def findAdjacentCells(space, cell: Cell) -> List[Cell]:
    '''see if there are open cells above, below, left, and right of cell'''

    x = cell[0]
    y = cell[1]
    adjacent_cells = []

    adjacent_cell = (x + 1, y)
    if adjacent_cell in space:
        adjacent_cells.append(adjacent_cell)
    adjacent_cell = (x, y + 1)
    if adjacent_cell in space:
        adjacent_cells.append(adjacent_cell)
    adjacent_cell = (x - 1, y)
    if adjacent_cell in space:
        adjacent_cells.append(adjacent_cell)
    adjacent_cell = (x, y - 1)
    if adjacent_cell in space:
        adjacent_cells.append(adjacent_cell)

    return adjacent_cells


def manhattanDistance(start, destination):
    return abs(start[0] - destination[0]) + abs(start[1] - destination[1])


def aStar(puzzle, start, destination, found_keys, path_cache) -> PathInfo:
    '''NEVER FAILS'''

    # path_cache_key = makePathCacheKey(start, destination, found_keys)
    # if path_cache_key in path_cache:
    #     path_cache["hits"] += 1
    #     return path_cache[path_cache_key]
    # path_cache["misses"] += 1

    space = puzzle["space"]
    frontier: List[Tuple[Cell, Any, int]] = [
        (start, None, 0)
    ]  # [(cell, path_parent, distance)]
    visited: Dict[Cell, Tuple[Cell,
                              int]] = {}  # cell -> (path_parent, distance)

    found_it = False
    current_cell = None
    while len(frontier) > 0:
        current_path_info = frontier.pop(0)
        current_cell = current_path_info[0]
        current_path_parent = current_path_info[1]
        distance_traveled = current_path_info[2]

        if current_cell not in visited:
            visited[current_cell] = (current_path_parent, distance_traveled)

        if current_cell == destination:
            found_it = True
            break

        adjacent_cells = findAdjacentCells(space, current_cell)
        for adjacent_cell in adjacent_cells:
            # check to see if we've already visited it
            if adjacent_cell in visited:
                visited_info = visited[adjacent_cell]
                # have we found a shorter path?
                if distance_traveled + 1 < visited_info[1]:
                    # shorter path! update that path info
                    visited[adjacent_cell] = (current_cell,
                                              distance_traveled + 1)
                    # don't forget to add it back to the frontier, all adjacent paths are now shorter
                    frontier.append(
                        (current_cell, current_cell, distance_traveled + 1))
                # continue regardless, either we will visit later or we won't
                continue

            char_at_adjacent_cell = space[adjacent_cell]

            # is it a door?
            if isDoor(char_at_adjacent_cell):
                # do we have the key?
                if char_at_adjacent_cell.lower() in found_keys:
                    # we can open it, add to next_frontier
                    frontier.append(
                        (adjacent_cell, current_cell, distance_traveled + 1))
            else:
                # no problem
                frontier.append(
                    (adjacent_cell, current_cell, distance_traveled + 1))

        # make sure frontier is always sorted so shortest distance is first
        frontier.sort(key=lambda x: manhattanDistance(x[0], destination))

    path_info = None
    if not found_it:
        path_info = ([], set(), set())
    elif current_cell == None:
        raise Exception("wut")
    else:
        path = []
        keys_passed = set()
        doors_passed = set()
        while True:
            path_info = visited[current_cell]
            if path_info[0] == None:
                break
            path.insert(0, current_cell)

            value_at_cell = space[current_cell]
            if isKey(value_at_cell):
                keys_passed.add(value_at_cell)
            elif isDoor(value_at_cell):
                doors_passed.add(value_at_cell)

            current_cell = path_info[0]
        path_info = (path, keys_passed, doors_passed)

    # path_cache[path_cache_key] = path_info

    return path_info


def travelPath(puzzle, current_cell, path, found_keys):
    space = puzzle["space"]
    if not path:
        return
    for cell in path:
        value_at_cell = space[cell]
        if isKey(value_at_cell):
            found_keys.add(value_at_cell)


def makePathCacheKey(start, destination, found_keys):
    found_keys = list(found_keys)
    found_keys.sort()
    return (start, destination, ','.join(found_keys))


def makeMemoCacheKey(puzzle):
    found_keys = list(puzzle["found_keys"])
    found_keys.sort()
    found_keys_string = ''.join(found_keys)
    locations_string = ','.join([
        "{},{}".format(region["current_location"][0],
                       region["current_location"][1])
        for region in puzzle["regions"]
    ])
    return (locations_string, found_keys_string)


def writeMemoCache(memo, puzzle, shortest_distance, next_destination):
    cache_value = (shortest_distance, next_destination)
    memo[makeMemoCacheKey(puzzle)] = cache_value


def readMemoCache(memo, puzzle):
    cache_key = makeMemoCacheKey(puzzle)
    if cache_key in memo:
        memo["hits"] += 1
        return memo[cache_key]
    memo["misses"] += 1
    return None


def printCaches(memo, path_cache):
    memo_info = "Memo Cache Hits: {} Misses: {}".format(
        memo["hits"], memo["misses"])
    path_info = "Path Cache Hits: {} Misses: {}".format(
        path_cache["hits"], path_cache["misses"])
    print(memo_info + ", " + path_info, end="\r")


def findShortestDistanceToAllKeys(puzzle, memo, path_cache):

    printCaches(memo, path_cache)

    cached_value = readMemoCache(memo, puzzle)
    if cached_value != None:
        return cached_value

    found_keys = puzzle["found_keys"]

    overall_shortest_distance = sys.maxsize
    overall_shortest_distance_cell = None

    # try every combination of robot moving next
    for region_index, region in enumerate(puzzle["regions"]):
        keys_in_region = region["keys"]

        # try every combination of keys in this region to travel to next
        for key in keys_in_region:

            if key in found_keys:
                continue

            key_cell = region["keys"][key]
            path_info: PathInfo = aStar(puzzle, region["current_location"],
                                        key_cell, puzzle["found_keys"],
                                        path_cache)
            if not path_info[0]:
                continue

            found_keys_copy = set(puzzle["found_keys"])
            found_keys_copy.update(path_info[1])

            regions_copy = []
            for i, region_copy in enumerate(puzzle["regions"]):
                if i == region_index:
                    regions_copy.append({
                        "keys": region["keys"],
                        "current_location": path_info[0][-1]
                    })
                else:
                    regions_copy.append(region_copy)

            puzzle_copy = {
                "regions": regions_copy,
                "found_keys": found_keys_copy,
                "space": puzzle["space"],
                "doors": puzzle["doors"],
            }

            shortest_distance_info = findShortestDistanceToAllKeys(
                puzzle_copy, memo, path_cache)

            total_distance_traveled = shortest_distance_info[0] + len(
                path_info[0])

            if total_distance_traveled < overall_shortest_distance:
                overall_shortest_distance = total_distance_traveled
                overall_shortest_distance_cell = path_info[0][-1]

    if overall_shortest_distance_cell == None:
        overall_shortest_distance = 0

    writeMemoCache(memo, puzzle, overall_shortest_distance,
                   overall_shortest_distance_cell)

    return (overall_shortest_distance, overall_shortest_distance_cell)


def getShortestDistanceForPuzzle(puzzle):
    memo = {}
    memo["hits"] = 0
    memo["misses"] = 0
    path_cache = {}
    path_cache["hits"] = 0
    path_cache["misses"] = 0
    shortest_distance = findShortestDistanceToAllKeys(puzzle, memo, path_cache)
    return shortest_distance


def solve(puzzle_input):
    # print("Parsing puzzle input...")
    # puzzle_input = puzzle_input.strip()
    # puzzle = parsePuzzleInput(puzzle_input)
    # shortest_distance = getShortestDistanceForPuzzle(puzzle)
    # print("\n")
    # print(shortest_distance)

    print("Building part2 puzzle input...")
    puzzle_input = puzzle_input.strip()
    puzzle = parsePuzzleInput(puzzle_input, True)
    shortest_distance = getShortestDistanceForPuzzle(puzzle)
    print("\n")
    print(shortest_distance)

    return


solve("""
#################################################################################
#z..........................#....k#.....#.......#.....#.............#...#.......#
#.###############.#########.#.###.#.###.#Q#######.#.###.#####.#####.#.#.#.#.###.#
#...#...#.....#...#.....#...#.#.#.#...#.#.#.......#..u#..i#.#...#.#.#.#...#...#j#
###W#.#.#####B#.#####.#.#.###.#.#.###.#.#.#.#########.###.#.###.#.#.#.#######.#.#
#.#...#.#...#.#.....#.#.......#.#...#.#.#...#...#.....#.#...#.#.#...#.#.....#.#.#
#.#####.#.#.#.#####.###########.###.#.#.#.###.#.#.###.#.###.#.#.#.#####.###.#.#.#
#...#...#.#.......#.......#.....#...#.#.#...#.#.#.#...#...#.#.#.#.#...#...#...#.#
#.#.#.###.#######.#######.###.###.#####.###.#.#.#.#.###.###.#.#.#.#.#.#.#.#####.#
#.#.#.....#.....#.#.......#...#...#.....#.#.#.#.#.#.....#...#.#.#...#.#.#...#...#
#.#.#######.###.#.#.#######.###.###.###.#.#.#.###.#######N###.#.#####.###.#.#.###
#.#...#...#...#...#.#...#.....#.#.....#.#...#...#.......#.#...#.....#...#.#.#.#.#
###.#.#.#.###.#####.#.#.#.###.#.#.###.#.#.#####.#######.#.###.#####.###.###.#.#.#
#...#.#.#...#.#...#.#.#...#...#.#.#...#.#.#.O...#.....#...#.....#...#.......#...#
#.###.#.#.###.###.#.###.###.###.#.#.###.#.#.#####.###.#.###.###.#.#############.#
#.#...#.#.........#...#...#.....#.#.#.#.#...#.....#...#.#...#.#.#.....#.........#
#.#####.#############.###.#####.###.#.#.###.#.#####.###.#.###.#.#####.#.#########
#.#...#.#.#.........#.#...#...#.....#...#...#.#...#.#.....#.........#.#.#.....#.#
#.#.#.#.#.#.#######.#.#####.#.###########.###.#.###.#################.#.#.###.#.#
#.#.#.#...#.#.....#...#...#.#.#.........#...#.#...#.......#.....#....w#.#.#.#.#.#
#.#.#.###.#.###.#.#.###.#.#.#.#.#######.###.#.#.#.#######.#.###.#.#####.#.#.#.#.#
#...#.#...#...#.#.#.#...#.#.#...#.#...#.#...#.#.#...#.......#.#...#...#...#.#.#.#
#.###.#.#####.#.###.#####.#.#####.#.#.#.#.###.###.#.#.#####.#.#####.#.#####.#.#.#
#...#.#.#...#.#.........#.#.#...#...#...#...#...#.#...#...#.#...#...#...#...#.#.#
#####.#.#.###.#.#######.#.#.###.#.#########.###.#######.#.#####.###.#####.#.#.#.#
#.....#.#...#.#.#...#...#...#...#.#.....#.#...#.#...#...#...#...#...#.....#...#.#
#.#.###.###.#.###.#.#.#######.#.#.#.###.#.###.#.#.#.#.#####.#.###.###M#########.#
#.#.#...#...#.....#.#...#.....#.#.#.#.#.#.#...#...#.#.#.....#.#.#...#.........#.#
#.###.###.#.#######.#####.#.#####.#.#.#.#.#.#######.#.#.###.#.#.#.#.#########.#.#
#.....#...#.#.....#.......#...#...#.#...#.#.#.....#.#.#.#...#.#...#...........#.#
#.#####.#.###.###.###########.#.###.#####.#.###.###.#.#.#####.#.#####.#######.#.#
#.#.....#.#...#.......#.....#...#...#...#.#...#...#.#.#.....#.#.#...#.#.....#...#
#.###.#.###.###.#####.###.#######.#.#.#.#.###.###.#.#.#####.#.###.#.###.###.#####
#...#.#.....#.#.....#...#.........#.#.#.#...#...#.#...#.....#.....#...#...#.....#
###.#######.#.#####.###.###.#########.#.###.###.#.#####.#############.###.#####.#
#.#...#...#...#...#...#...#.....#.....#.#.....#.......#.#...#.......#.....#.D.#.#
#.###.#.#.###.###.###.###.###.#.#.#####.#.###.#####.###.#.#.#.###.#.#########.#.#
#...#...#...#.......#...#.E.#.#...#...#.#...#.#.....#...#.#...#...#.#.........#c#
#.#.#######.###########.###.#######.#.#.#.#.###.#####.###.#####.#####.#####.###.#
#.#.....................#...........#.....#.........#.........#...........#.....#
#######################################.@.#######################################
#.......#.....#.........#...........#.............#.....#...#.......#...........#
#.#####.#.###.#.#####.###.#####.###.###.#.###.###.###.###.#.#.#.###.#.#####.###.#
#.#...#.#.#...#.T...#.....#...#.#.....#.#.#...#.#.....#...#.#.#.#...#....a#...#.#
#.#.#.###.#.#######.#####.#.#.#.#####.#.#.#.###.#####.#.###.#.#.#########.###.#.#
#...#.....#.........#...#...#.#.....#...#.#.#........e#...#...#.S.#.......#...#.#
#####################.#.###########.###.#.#.#.###########.#######.#.#######.###.#
#d..#...#.........C...#.#.......#...#...#.#.#.#.........#.#.#.....#.#...#...#..y#
#.#.#.#.#.#########.###.#.#####.#.###.###.#.###.#######.#.#.#.#####.###.#.###.###
#.#.#.#.......#...#.#...#.#.....#.#...#.#.#...#...#...#...#.#.....#.#...#.#.....#
#.#.#.#########.#.###.###.###.###.#.###.#.###.###.#.#######.#####.#.#.###.#####.#
#.#...#.#.......#.#.G.#.....#.....#...#.#.#...#...#.....#.....#.#...#...#.....#.#
#.#####.#.#######.#.###.###.#########.#.#.#.###.#####.#.#.#.#.#.#######.#####.#.#
#.#.....#.#.........#...#.#.....#...#.#.#.#.#...#...#.#.#.#.#.#.......#.....#.#.#
#Y###.###F#############.#.#####.###.#.#.#.#.#.###.#.#.#.###.#.#####.#.#####.#.#.#
#...#.#...#.....P.....#.......#...#.....#.#.#.....#...#.....#.#.....#.#.....#.#.#
###.#.#.#.#.#########.#######.###.#####.###.#################.#.#####.#.#####.#.#
#...#.#.#.#r#.........#.........#.....#.#...#...#o..........#...#.......#.....#.#
#.###.#.###.#######.###############.#.###.###.#.#.#.#####.###.###########.#####.#
#.#...#...#.......#.....#...#.....#.#...#.....#.#.#.....#.#...#........p#.#...#.#
#.#.#.###.#######.#####.#.#.#.###.#####.#.#####.#.#####.###.###.#######.#.#.###.#
#...#.A.#...X...#.#...#.#.#...#.#.#...#.#..t#.#...#...#...#.#...#...#...#.#.....#
#######.#######.#.#R###.#.#####.#.#.#.#.###.#.#####.#####.#.#####.#.#.###.#######
#.#.....#...#...#...#...#...#.#...#.#...#.#.........#q....#.#...#.#...#.........#
#.#.#####.###.#######V###.#.#.#.###.#####.#########.#.#####.#.#.#.#########.###.#
#.#.#.....#...#.....#...#.#.#...#.......#...#.......#.....#.#.#.#v#.......#...#.#
#.#.#.#.###.#.#.#.#.###.#.#.#.#####.###.#.#.#.###########.#.###.#.###.###.###.#.#
#.#.#.#.#...#.#.#.#.#...#.#.#.#...#...#.#.#.#.......#...#.#b..#.#.#...#.#...#.#.#
#.#.#.#.#.###.#.#.###.#####.#.#.#.#####.###.#.#######.#.#.###.#.#.#.###.###.###.#
#...#.#m#...#.#l#.....#.....#.I.#.#...#.#...#.#.......#.....#...#.#.#g....#.#...#
#.#####.###.#.#.#########.#######.#.#.#.#.###.#.#############.###.#.#####.#.#.#.#
#.#.......#.#.#...#.....#.#.#...#...#.#.#...#.#.....#.........#...#....f#.....#.#
#.#.#####.#.#####.#.#.#.#.#.#.#.#####.#.#.#.#.#####.#.#########L#######.#########
#.#...#.#.#.....H.#.#.#...#...#.#...#.#.#.#.....#...#...#.......#.....#.........#
#.###.#.#.#########.#.#####.###.#.#.#.#.#.#######.#####.#.#######.###.#.#######.#
#.....#.#.#...#.....#.Z...#...#.#.#...#.#.#...#...#.....#...#.#.....#.#.......#.#
#######.#.#.#.#.#####.###.###.#.#.#####.#.#.#.#.#U#.#######.#.#.###.#.#########.#
#..s......#.#.#.#...#...#.#...#.#.......#...#.#.#.#...#.....#.....#.#.....#.....#
#.#########.#.###.#.#####.#.###.#######.#####.#.#####.#.###########.#####.#.###.#
#.......K...#...J.#.......#...#........n#.....#.......#............h#......x#...#
#################################################################################
""")