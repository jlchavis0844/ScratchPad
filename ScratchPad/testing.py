import os, sys
import win32com.client 


finished = 13

oldBaseIDs = [1,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,5,5,55,5,5,5,5,5,5,5,58,8,7,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,5,5,55,5,5,5,5,5,5,5,58,8,7]
m, s = divmod(((len(oldBaseIDs) - finished)*3), 60)
h, m = divmod(m, 60)
remaining = ("%02d:%02d:%02d" % (h, m, s))
print("Working:" + "{0:.2f}".format((finished/ len(oldBaseIDs))*100) + "% Done, Remaining(h:m:s): " + remaining)