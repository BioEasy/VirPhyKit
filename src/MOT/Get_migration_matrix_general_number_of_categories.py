#!/usr/bin/env python
from ete3 import Tree
import sys
import csv
import math
def FindPlacement(height, length):
    end = int( math.ceil(rootheight) - math.ceil(height))
    start = int( end - math.floor(length) )
    return start, end

def FindRow(parentloc, thisloc, unique_locs):
    try:
        parentloc_index = unique_locs.index(parentloc)
        this_index = unique_locs.index(thisloc)
    except ValueError:
        sys.exit("Invalid parent-daughter: %s, %s" % (parentloc, thisloc))

    return parentloc + "_to_" + thisloc

def FindLocationOfParent(node):
    parent = node.up
    try:
        return infodic[parent.name]["location"]
    except AttributeError:
        sys.exit("Error finding parent of %s" % node.name)
tree = Tree(sys.argv[1], format=1)
rootheight = tree.get_farthest_node()[1]
print("Tree height: %s" % rootheight)



infodic = {}

with open(sys.argv[2],"r") as infofile:
    csvreader = csv.reader(infofile, delimiter=",")
    header = next(csvreader)
    for row in csvreader:
        infodic[row[0]] = {"height": row[1], "length":row[2],"location":row[3], "countryprob":row[4],"isolate":row[5]}
unique_locs = list( sorted( set( [infodic[sub]["location"] for sub in infodic] ) ) )
num_unique_locs = len(unique_locs)
isolates = list( sorted( set( [infodic[sub]["isolate"] for sub in infodic] ) ) )
mostcurrentyear = int(isolates[-2][:4])
rootyear = int(mostcurrentyear - math.ceil(rootheight))

print("Most current year: %s" % mostcurrentyear)
print("Year of the root: %s" % rootyear)

row_keys = [fromloc + "_to_" + toloc for fromloc in unique_locs for toloc in unique_locs]
column_keys = list(range(rootyear,mostcurrentyear+1))
calendar = {r: {c:0 for c in column_keys} for r in row_keys}
for node in tree.iter_descendants("preorder"):
    try:
        nodeheight = float(infodic[node.name]["height"])
    except KeyError:
        sys.exit("Could not find in infodic: %s" % node.name)
    nodelength = float(infodic[node.name]["length"])
    nodelocation = infodic[node.name]["location"]
    nodestart, nodeend = FindPlacement(nodeheight,nodelength)
    nodestart += rootyear
    nodeend += rootyear
    nodeparentloc = FindLocationOfParent(node)
    row = FindRow(nodeparentloc, nodelocation, unique_locs)
    for z in range(nodestart,nodeend+1):
        try:
            calendar[row][z] += 1
        except KeyError:
            print(z)
            print(node)
            sys.exit(-1)


with open(sys.argv[3],"w") as outfile:
    csvwriter = csv.writer(outfile,delimiter=",")
    csvwriter.writerow([""] + column_keys)
    for transition in row_keys:
        writelist = [transition]
        #csvwriter.writerow(calendar[transition])
        for year in column_keys:
            writelist.append(calendar[transition][year])
        csvwriter.writerow(writelist)



