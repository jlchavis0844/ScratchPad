from os import listdir
from os.path import isfile, join
mypath = 'S:\\1TDS Enrollments\\Saratoga\\2018\\'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]


with open('H:\\Logs\\Test.txt', 'w') as myfile:
    for x in onlyfiles:
        myfile.write(x)
        print(x)

print('Done')