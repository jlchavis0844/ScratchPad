import os, sys
import win32com.client 

shell = win32com.client.Dispatch("WScript.Shell")
logLocation = r'C:\apps\test.csv'
searchLocation = "\\\\nas3\\tds\\HD"

f = open(logLocation, 'w')

for root, subfolders, files in os.walk(searchLocation):
    for file in files:
        thisFile = os.path.join(root,file).replace(",","_")
        if ".lnk" in thisFile:
            try:
                shortcut = shell.CreateShortCut(thisFile)
                msg = thisFile + ", " + shortcut.Targetpath.replace(",","_")
                if os.path.exists(shortcut.Targetpath):
                    msg += ", TRUE\n"
                else:
                    msg += ",FALSE\n"
                print(msg)
                f.write(msg)
            except:
                print("could not open: " + thisFile)
f.close()