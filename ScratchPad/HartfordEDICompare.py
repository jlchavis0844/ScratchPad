'''
This module loads in two | (pipe) delimited files, removes the first and
last lines (header and footer) and then compares the remaining lines
to see if there are differences. If a line is found to be different, 
all lines are then rechecked token (split on pipe) to find the difference.
if a line is different, all tokens for that line are checked.
lines are sorted by name if differences are found.
TODO: only check lines that are different to remove redundancy.
'''
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class Line:
    def __init__(self, inStr):
        self.tokens = inStr.split('|')
        self.id = self.tokens[5]
        self.name = (self.tokens[8] + ' ' + self.tokens[7]).strip()
        self.line = inStr

def LineKey(Line):
    return Line.name

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename(initialdir = "C:\\Hartford_prod\\",title = "open file 1") # show an "Open" dialog box and return the path to the selected file
if not filename:
    exit()
    
with open(filename, "r") as fp:
    lines1 = fp.readlines()
    
filename = askopenfilename(initialdir = "C:\\Hartford_prod\\",title = "open file 2")
if not filename:
    exit()

with open(filename,'r') as fp:
    lines2 = fp.readlines()
    

lines1.pop(0)
lines1 = lines1[:-1]
lines2.pop(0)
lines2.pop(len(lines2)-1)

useList1 = len(lines1) >= len(lines2)
# for idx, val in enumerate(lines1):
#     if idx != 0 and (idx + 1) < len(lines1):
#         print(Line(val).name)
go = len(lines1) == len(lines2)
if useList1:
    for idx, val in enumerate(lines1):
        if go and (idx + 1) < len(lines1) \
        and (idx + 1) < len(lines1) \
        and (idx + 1) < len(lines2):
            if lines1[idx] != lines2[idx]:
                print("mismatch:\n" + lines1[idx] + '\n' + lines2[idx])
                go = False
else:
    for idx, val in enumerate(lines2):
        if go and (idx + 1) < len(lines2) \
        and (idx + 1) < len(lines2) \
        and (idx + 1) < len(lines1):
            if lines1[idx] != lines1[idx]:
                print("mismatch:\n" + lines2[idx] + '\n' + lines1[idx])
                go = False

if not go:
    print('going to find what is different')
    
    l1o = [];
    for inx, val in enumerate(lines1):
        thisLine = Line(val)
        l1o.append(thisLine)
        
    l2o = [];
    for inx, val in enumerate(lines2):
        thisLine = Line(val)
        l2o.append(thisLine)

    l1o_sorted = sorted(l1o, key=LineKey)
    l2o_sorted = sorted(l2o, key=LineKey)
    
    cntr = 0;
    if useList1:
        try:
            while cntr < len(l1o_sorted):
                if l1o_sorted[cntr].line != l2o_sorted[cntr].line:
                    tcntr = 0
                    while tcntr < len(l1o_sorted[cntr].tokens):
                        if str(l1o_sorted[cntr].tokens[tcntr]) != str(l2o_sorted[cntr].tokens[tcntr]):
                            print ("for " + l2o_sorted[cntr].name + ": \"" + str(l2o_sorted[cntr].tokens[tcntr]) + "\" != \"" \
                                   + str(l1o_sorted[cntr].tokens[tcntr]) + "\"")
                        tcntr = tcntr + 1
                cntr = cntr + 1
        except:
            print("#ERROR")
    else:
        try:
            while cntr < len(l2o_sorted):
                if l2o_sorted[cntr].line != l1o_sorted[cntr].line:
                    tcntr = 0
                    while tcntr < len(l1o_sorted[cntr].tokens):
                        if str(l1o_sorted[cntr].tokens[tcntr]) != str(l2o_sorted[cntr].tokens[tcntr]):
                            print ("for " + l2o_sorted[cntr].name + ": \"" + str(l2o_sorted[cntr].tokens[tcntr]) + \
                                   "\" != \"" + str(l1o_sorted[cntr].tokens[tcntr]) + "\"")
                        tcntr = tcntr + 1
                cntr = cntr + 1
        except:
            print("#ERROR")

if not go:
    input("Differences found. Press Enter to exit...")
else:
    print("All done. No differences found.")
            
            
            
            
            
            