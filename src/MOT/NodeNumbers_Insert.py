#!/usr/bin/env python

# Modified from 
# Global L4 scripts:A collection of scripts used for the global L4 MTB phylogeography paper
# by Ola Brynildsrud (ola.brynildsrud@fhi.no)

import sys
import re
import itertools

with open(sys.argv[1],"r") as infile:
    inf = infile.read()
    nodes = re.findall("\d+\[",inf)
    nodenumbers = [int(n.rstrip("[")) for n in nodes]
    maxnode = max(nodenumbers)
    start = maxnode + 1
    cnt = itertools.count(start)

    with open(sys.argv[2],"w") as outfile:
        outstring = re.sub(r"\)", lambda x: "){}".format(next(cnt)), inf)
        outfile.write(outstring)

