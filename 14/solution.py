from typing import Dict, Tuple, List

Compound = Tuple[int, str]  # (coefficient, formula)
Reaction = Tuple[List[Compound], Compound]  # ([reagants], output)


def solve(input_string):
    def parseCompound(input) -> Compound:
        parts = input.split(" ")
        return (int(parts[0]), str(parts[1]))

    '''WE ASSUME ONE OUTPUT'''

    def parseReaction(input) -> Reaction:
        parts = line.split(" => ")
        input_reagents: List[Compound] = [
            parseCompound(i) for i in parts[0].split(", ")
        ]
        output: Compound = parseCompound(parts[1])
        return (input_reagents, output)

    # parse input
    '''WE ASSUME ONLY ONE REACTION PER OUTPUT'''
    reactions_by_output: Dict[str, Reaction] = {}
    '''WE ASSUME NO CYCLES'''
    reaction_feed_forward_map: Dict[str, List[str]] = {}
    for line in input_string.split("\n"):
        reaction = parseReaction(line)
        reactions_by_output[reaction[1][1]] = reaction

        for reagent in reaction[0]:
            feed_forward: List[str] = []
            if reagent[1] in reaction_feed_forward_map:
                feed_forward = reaction_feed_forward_map[reagent[1]]
            feed_forward.append(reaction[1][1])
            reaction_feed_forward_map[reagent[1]] = feed_forward

    def calculateReactionCount(desired_output: int, output_coefficient: int):
        if desired_output < output_coefficient:
            return 1
        else:
            total = desired_output // output_coefficient
            total += int(desired_output % output_coefficient > 0)
            return total

    def determineNumberOfFormulaNeeded(formula: str, desiredFuel,
                                       memo: Dict[str, int]) -> int:
        '''
        Walk up the reaction tree from the specified formala until we reach an end state (FUEL).
        Then walk back down, at each point determining how many of the spcecified formula we will need,
        given how many dependent reactions we need to perform.
        '''

        if formula == "FUEL":
            return desiredFuel
        total = 0
        for feed_forward in reaction_feed_forward_map[formula]:
            if feed_forward in memo:
                required_output = memo[feed_forward]
            else:
                required_output = determineNumberOfFormulaNeeded(
                    feed_forward, desiredFuel, memo)
                memo[feed_forward] = required_output
            reaction = reactions_by_output[feed_forward]
            for reagant in reaction[0]:
                if reagant[1] == formula:
                    number_reactions = calculateReactionCount(
                        required_output, reaction[1][0])
                    total += number_reactions * reagant[0]
                    break

        return total

    def getMinimumRequiredOreForFuel(desiredFuel):
        # for each compound that is created from ore, tell how many we need
        # then calculate how much ore we need
        minimum_required_ore = 0
        memo = {}
        for formula in reaction_feed_forward_map["ORE"]:
            total_formula = determineNumberOfFormulaNeeded(
                formula, desiredFuel, memo)
            memo[formula] = total_formula
            reaction = reactions_by_output[formula]
            coefficient_of_output = reaction[1][0]
            coefficient_of_ore = reaction[0][0][0]  # assumptions!
            number_reactions = calculateReactionCount(total_formula,
                                                      coefficient_of_output)
            minimum_required_ore += number_reactions * coefficient_of_ore

        return minimum_required_ore

    def getMaximumFuelForAvailableOre(total_available_ore):
        '''
        Brute Force (kind of). Just count up from some arbitrary fuel value, increasing
        or decreasing proportionally given how far the required ore is from the total 
        available ore
        '''
        i = 1000
        closest_ore = 0
        closest_fuel = 0
        times_same_ore_requirement = 0
        while True:
            minimumRequiredOre = getMinimumRequiredOreForFuel(i)

            if minimumRequiredOre == closest_ore:
                times_same_ore_requirement += 1
            else:
                times_same_ore_requirement = 0

            if times_same_ore_requirement == 1000:
                break

            if minimumRequiredOre < total_available_ore:
                if (minimumRequiredOre > closest_ore):
                    closest_ore = minimumRequiredOre
                    closest_fuel = i
            elif minimumRequiredOre == total_available_ore:
                closest_fuel = i
                break

            difference = (total_available_ore -
                          minimumRequiredOre) / total_available_ore
            i += int(i * difference)

        return closest_fuel

    print(getMinimumRequiredOreForFuel(1))

    print(getMaximumFuelForAvailableOre(1000000000000))

    return


solve("""13 WDSR, 16 FXQB => 6 BSTCB
185 ORE => 9 BWSCM
1 WDSR => 9 RLFSK
5 LCGL, 7 BWSCM => 9 BSVW
6 NLSL => 3 MJSQ
1 JFGM, 7 BSVW, 7 XRLN => 6 WDSR
3 WZLFV => 3 BZDPT
5 DTHZH, 12 QNTH, 20 BSTCB => 4 BMXF
18 JSJWJ, 6 JLMD, 6 TMTF, 3 XSNL, 3 BWSCM, 83 LQTJ, 29 KDGNL => 1 FUEL
1 LWPD, 28 RTML, 16 FDPM, 8 JSJWJ, 2 TNMTC, 20 DTHZH => 9 JLMD
1 SDVXW => 6 BPTV
180 ORE => 7 JFGM
13 RLFSK, 15 HRKD, 1 RFQWL => 5 QNTH
1 RFQWL, 3 NZHFV, 18 XRLN => 9 HRKD
2 NLSL, 2 JXVZ => 5 GTSJ
19 SDVXW, 2 BSVW, 19 XRLN => 6 QMFV
1 CSKP => 8 LQTJ
4 ZSZBN => 5 RBRZT
8 WZLFV, 3 QNWRZ, 1 DTHZH => 4 RTRN
1 CGXBG, 1 PGXFJ => 3 TNMTC
4 CGCSL => 7 RNFW
9 CGCSL, 1 HGTL, 3 BHJXV => 8 RSVR
5 NGJW => 8 HTDM
21 FPBTN, 1 TNMTC, 2 RBRZT, 8 BDHJ, 28 WXQX, 9 RNFW, 6 RSVR => 1 XSNL
2 WZLFV => 5 BHJXV
10 BSTCB, 4 NLSL => 4 HQLHN
1 JFGM => 7 SDVXW
6 CSKP => 8 FXQB
6 TNMTC, 4 BZDPT, 1 BPTV, 18 JSJWJ, 2 DTHZH, 1 LWPD, 8 RTML => 8 KDGNL
6 XFGWZ => 7 CGCSL
3 GTSJ => 4 LWPD
1 WDSR, 1 QNWRZ => 5 XFGWZ
11 CSKP, 10 SDVXW => 4 QNWRZ
7 BSVW, 4 QMFV => 1 RFQWL
12 QNTH, 10 HTDM, 3 WXQX => 3 FDPM
2 HGTL => 7 PGXFJ
14 SDVXW => 6 CSKP
11 HQLHN, 1 GTSJ, 1 QNTH => 5 TMTF
173 ORE => 9 LCGL
4 WXQX => 9 BDHJ
5 BZDPT => 7 NGJW
1 GTSJ, 23 QNWRZ, 6 LQTJ => 7 JSJWJ
23 NZHFV, 3 HQLHN => 6 DTHZH
2 JFGM => 4 XRLN
20 CGCSL => 9 WXQX
2 BSTCB, 3 HRKD => 9 NLSL
1 MJSQ, 1 BPTV => 8 CGXBG
1 RTRN, 1 RSVR => 3 ZSZBN
2 NZHFV, 1 BSTCB, 20 HRKD => 1 JXVZ
2 BZDPT => 5 HGTL
1 ZSZBN, 14 FDPM => 9 RTML
3 BMXF => 8 FPBTN
1 SDVXW, 8 XRLN => 9 NZHFV
18 QNWRZ, 7 RLFSK => 1 WZLFV""")