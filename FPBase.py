
#FIRST LP: INCLUSION
#1. Reads a file for data.
#2. LP "Include" chooses a given number of songs that maximizes satisfaction from given data.

import pulp
from pathlib import Path

def read_input1(in_file):
    return

input_fname = ""   
PLAYLIST_LENGTH = 4

include = pulp.LpProblem("include",pulp.LpMaximize)

#creating variables out of below test data. Format any data with <songname>_<artist>_<score>
test_data = [("The Spinning Continuous","The Olivia Tremor Control",4),("Two-Headed Boy", "Neutral Milk Hotel", 5),("YAMAPIKARYA!!!", "Zhnoi", 2), ("Tusk", "Fleetwood Mac", 4), ("Hazel", "Far Apart", 4), ("half enough", "key vs. locket", 3)]
vars = []
for var in range(len(test_data)):
    vars.append(include.add_variable(test_data[var][0]+"$"+test_data[var][1]+"$"+str(test_data[var][2]), cat=pulp.LpBinary))

#Ensures number selected less than given playlist length.
#Additionally adds the total score of selected songs and sets objective
total_included = 0
total_score = 0
for var in vars:
    total_included += var
    total_score += int(var.name[-1]) * var
include.addConstraint(total_included <= PLAYLIST_LENGTH)
include.setObjective(total_score)

#Solves which songs to include from given data and writes playlist to a file.
status1 = include.solve()
with open(Path(__file__).parent / "included_songs.txt", "w") as solution:
    for var in vars:
        if var.varValue == 1:
            print(var)
            solution.write(var.name+"\n")
print("Total Satisfaction: " + str(pulp.value(total_score)))


#SECOND LP: ORDERING
#Sequences the chosen songs from the above (inclusion) LP to maximize the average between two consecutive songs.

def read_input2(in_file):
    output = []
    fin = open(in_file, "r")
    for line in fin.read().split("\n"):
        output.append(line.split("$"))
    fin.close()
    return output[:-1]

inputs = read_input2(Path(__file__).parent / "included_songs.txt")
#print(inputs)

#Set up LP2 (sequence) and adds a variable for each slot in a nxn matrix for n songs.
sequence = pulp.LpProblem("sequence",pulp.LpMaximize)
vars = []
for y in range(len(inputs)):
    row = []
    for x in range(len(inputs)):
        row.append(sequence.add_variable(str(y)+"$"+str(x), cat=pulp.LpBinary))
    vars.append(row)

#Makes sure each song can only be chosen once and only one song can be in each position
for y in range(len(inputs)):
    positions = 0
    for x in range(len(inputs)):
        positions += vars[y][x]
    sequence.addConstraint(positions == 1)
for x in range(len(inputs)):
    positions = 0
    for y in range(len(inputs)):
        positions +=vars[y][x]
    sequence.addConstraint(positions == 1)

average_score = 0

for x in range(len(inputs)-1):
    for a in range(len(inputs)):
        for b in range(len(inputs)):
            if not (a == b):
                consecutive_pair = sequence.add_variable(f"({a},{b})@{x}", cat=pulp.LpBinary)
                #If position n+1 is used, position n is also used:
                sequence.addConstraint(consecutive_pair <= vars[a][x])
                sequence.addConstraint(consecutive_pair <= vars[b][x+1])
                sequence.addConstraint(consecutive_pair >= vars[a][x] + vars[b][x+1] - 1)

                tempavgscore = (float(inputs[a][2])+float(inputs[b][2]))/2.0
                average_score += tempavgscore * consecutive_pair

sequence.setObjective(average_score)

status2 = sequence.solve()


print("Total Average: "+str(pulp.value(average_score)))

with open(Path(__file__).parent / "maximize_average_order.txt", "w") as solution:
    for x in range(len(inputs)):
        for a in range(len(inputs)):
            if vars[a][x].varValue == 1:
                print(f"Position {x + 1}: {'$'.join(inputs[a])}")
                solution.write(f"{'$'.join(inputs[a])}"+"\n")

