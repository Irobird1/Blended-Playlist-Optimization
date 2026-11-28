


import pulp
from pathlib import Path

def read_input1(in_file):
    return

def LP_select_songs():
    """ FIRST LP: INCLUSION
    
        Chooses a given number of songs that maximizes satisfaction from given data
    """
    input_fname = ""
    #read_input1(input_fname)
    PLAYLIST_LENGTH = 4

    # TEST DATA
    # Format any additional data with <songname>_<artist>_<score>
    test_data = [("The Spinning Continuous", "The Olivia Tremor Control",4),
                 ("Two-Headed Boy", "Neutral Milk Hotel", 5),
                 ("YAMAPIKARYA!!!", "Zhnoi", 2),
                 ("Tusk", "Fleetwood Mac", 4),
                 ("Hazel", "Far Apart", 4),
                 ("half enough", "key vs. locket", 3)]

    # LP definition
    include = pulp.LpProblem("include", pulp.LpMaximize)

    # Creating LP variables
    vars = []
    for var in range(len(test_data)):
        vars.append(include.add_variable(test_data[var][0]+"$"+test_data[var][1]+"$"+str(test_data[var][2]), cat=pulp.LpBinary))

    # Creating LP constraints
    total_included = pulp.lpSum(vars)
    include.addConstraint(total_included <= PLAYLIST_LENGTH)

    # Setting LP objective
    total_score = pulp.lpSum(var.name[-1] * var for var in vars)
    include.setObjective(total_score)

    # Solves which songs to include from given data and writes playlist to a file
    status1 = include.solve()
    #status1 = include.solve(pulp.PULP_CBC_CMD())    #### For Jason and Robert
    with open(Path(__file__).parent / "included_songs.txt", "w") as solution:
        for var in vars:
            if var.varValue == 1:
                print(var)
                solution.write(var.name+"\n")
    print("Total Satisfaction: " + str(pulp.value(total_score)))


def read_input2(in_file):
    """ Parses input file into a list of lists """
    output = []
    fin = open(in_file, "r")
    for line in fin.read().split("\n"):
        output.append(line.split("$"))
    fin.close()
    return output[:-1]

def LP_order_songs_avg_score2():
    """ SECOND LP: ORDERING

        Sequences the chosen songs from the inclusion LP to maximize the average between two consecutive songs
    """
    inputs = read_input2(Path(__file__).parent / "included_songs.txt")
    #print(inputs)

    # LP definition
    sequence = pulp.LpProblem("sequence", pulp.LpMaximize)

    # LP variables
    ## Adds a variable for each slot in a nxn matrix for n songs
    ## Rows (y) = the song
    ## Columns (x) = the spot in the rotation
    vars = []
    for y in range(len(inputs)):
        row = []
        for x in range(len(inputs)):
            row.append(sequence.add_variable(str(y)+"$"+str(x), cat=pulp.LpBinary))
        vars.append(row)
    min_average = sequence.add_variable("min_avg", lowBound=None, cat=pulp.LpContinuous)

    # LP constraints and objective
    ## Each song must be chosen exactly once
    for y in range(len(inputs)):
        positions = 0
        for x in range(len(inputs)):
            positions += vars[y][x]
        sequence.addConstraint(positions == 1)
    ## Each position must have exactly one song
    for x in range(len(inputs)):
        positions = 0
        for y in range(len(inputs)):
            positions +=vars[y][x]
        sequence.addConstraint(positions == 1)
    ## Identify consecutive songs
    average_score = 0
    for x in range(len(inputs)-1):
        for a in range(len(inputs)):
            for b in range(len(inputs)):
                if not (a == b):
                    # consecutive_pair = 1 when this ordered pair is used and 0 otherwise
                    consecutive_pair = sequence.add_variable(f"({a},{b})@{x}", cat=pulp.LpBinary)
                    # consecutive_pair can only be 1 when used by both
                    sequence.addConstraint(consecutive_pair <= vars[a][x])
                    sequence.addConstraint(consecutive_pair <= vars[b][x+1])
                    # consecutive_pair must be 1 when used by both
                    sequence.addConstraint(consecutive_pair >= vars[a][x] + vars[b][x+1] - 1)

                    # Score = score for song * if we use it
                    twosongavgscore = (float(inputs[a][2]) + float(inputs[b][2]))/2.0
                    sequence.addConstraint(min_average <= twosongavgscore + 20 * (1 - consecutive_pair))
    sequence.setObjective(min_average)

    # Solves the order of songs and writes to a file
    #status = sequence.solve()
    status = sequence.solve(pulp.PULP_CBC_CMD())    #### For Jason and Robert
    print("Total Average: "+str(pulp.value(average_score)))
    with open(Path(__file__).parent / "maximize_average_order.txt", "w") as solution:
        for x in range(len(inputs)):
            for a in range(len(inputs)):
                if vars[a][x].varValue == 1:
                    print(f"Position {x + 1}: {'$'.join(inputs[a])}")    # Use x + 1 to move from 0 to 1 index
                    solution.write(f"{'$'.join(inputs[a])}"+"\n")


def LP_order_songs_avg_score3():
    """ SECOND LP: ORDERING

        Sequences the chosen songs from the inclusion LP to maximize the average between three consecutive songs
    """
    inputs = read_input2(Path(__file__).parent / "included_songs.txt")
    #print(inputs)

    # LP definition
    sequence = pulp.LpProblem("sequence", pulp.LpMaximize)

    # LP variables
    ## Adds a variable for each slot in a nxn matrix for n songs
    ## Rows (y) = the song
    ## Columns (x) = the spot in the rotation
    vars = []
    for y in range(len(inputs)):
        row = []
        for x in range(len(inputs)):
            row.append(sequence.add_variable(str(y)+"$"+str(x), cat=pulp.LpBinary))
        vars.append(row)
    min_average = sequence.add_variable("min_avg", lowBound=None, cat=pulp.LpContinuous)

    # LP constraints and objective
    ## Each song must be chosen exactly once
    for y in range(len(inputs)):
        positions = 0
        for x in range(len(inputs)):
            positions += vars[y][x]
        sequence.addConstraint(positions == 1)
    ## Each position must have exactly one song
    for x in range(len(inputs)):
        positions = 0
        for y in range(len(inputs)):
            positions +=vars[y][x]
        sequence.addConstraint(positions == 1)
    ## Identify consecutive songs
    average_score = 0
    for x in range(len(inputs)-2):
        for a in range(len(inputs)):
            for b in range(len(inputs)):
                for c in range(len(inputs)):
                    if not (a == b) and not (a == c) and not (b == c):
                        # consecutive_pair = 1 when this ordered pair is used and 0 otherwise
                        consecutive_pair = sequence.add_variable(f"({a},{b},{c})@{x}", cat=pulp.LpBinary)
                        # consecutive_pair can only be 1 when used by both
                        sequence.addConstraint(consecutive_pair <= vars[a][x])
                        sequence.addConstraint(consecutive_pair <= vars[b][x+1])
                        sequence.addConstraint(consecutive_pair <= vars[c][x+2])
                        # consecutive_pair must be 1 when used by both
                        sequence.addConstraint(consecutive_pair >= vars[a][x] + vars[b][x+1] + vars[c][x+2] - 2)

                        # Score = score for song * if we use it
                        threesongavgscore = (float(inputs[a][2]) + float(inputs[b][2]) + float(inputs[c][2]))/3.0
                        sequence.addConstraint(min_average <= threesongavgscore + 20 * (1 - consecutive_pair))
    sequence.setObjective(min_average)

    # Solves the order of songs and writes to a file
    #status = sequence.solve()
    status = sequence.solve(pulp.PULP_CBC_CMD())    #### For Jason and Robert
    print("Total Average: "+str(pulp.value(average_score)))
    with open(Path(__file__).parent / "maximize_average_order.txt", "w") as solution:
        for x in range(len(inputs)):
            for a in range(len(inputs)):
                if vars[a][x].varValue == 1:
                    print(f"Position {x + 1}: {'$'.join(inputs[a])}")    # Use x + 1 to move from 0 to 1 index
                    solution.write(f"{'$'.join(inputs[a])}"+"\n")






#LP_order_songs_avg_score2()
LP_order_songs_avg_score3()