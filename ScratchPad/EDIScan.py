'''
This script will scan a Guardian EDI file and check most of the currently
used fields to see whether they are in the valid, tab-delimited format
according the Guardian's specification file.
'''
import datetime, json, requests, sys, os, csv, ctypes
import tkinter  # for the file picker
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime

'''
A simple function that returns whether the given substring can be 
converted into a valid integer
This method uses simple try/catch on conversion
note: the start is inclusive and stop is exclusive so line='1234',
 start=1, stop=4 will result in int('23')= True
@param line - String of the text we will be taking the substring 
from
@param start - int of the first char to start the substring 
(inclusive)
@param stop - int of the char to stop the subdivision of the 
substring (exclusive)
@return boolean on whether the substring can be converted 
'''
def checkNum(line, start, stop):
    try:
        if line[start:stop].strip() != "":
            int(line[start:stop].strip())
        return True
    except ValueError:
        return False
    
'''
A simple function that returns whether the given substring can be 
converted into a valid phone number. Check num doesn't work since 
phone numbers will need to replace "-".
@param line - String of the text we will be taking the substring 
from
@param start - int of the first char to start the substring 
(inclusive)
@param stop - int of the char to stop the subdivision of the 
substring (exclusive)
@return boolean on whether the substring can be converted 
'''
def checkPhone(line, start, stop):
    try:
        testNum = line[start:stop].strip().replace("-","") 
        if testNum != "":
            int(testNum)
        return True
    except ValueError:
        return False

'''
A function that attempts to convert a substring into a date in 
the format of YYYYMMDD.Failure means that it is not a proper date,
relies on datetime.datetime.strptime
@param line - string of the text we will be taking the substring 
from
@param start - int of the first char to start the substring 
(inclusive)
@param stop - int of the char to stop the subdivision of the 
substring (exclusive)
@return boolean on whether the substring can be converted 
'''
def checkDate(line, start, stop):
    try:
        if line[start:stop].strip() != "":
            datetime.strptime(line[start:stop].strip(),'%Y%m%d')
        return True
    except ValueError:
        return False

path = os.path.dirname(__file__)  # get current path
# get timestamp for the log writing.
time = datetime.now().strftime('%Y-%m-%d_%H%M%S') 
    
if len(sys.argv) > 1:
    if os.path.isfile(sys.argv[1]):
        edi_path = sys.argv[1]
    else:
        input("The given file argument is not a valid file, press enter to continue")
        exit()
else:  
    # optional stuff for the file picker
    FILEOPENOPTIONS = dict(defaultextension='.txt', filetypes=[('EDI file', 
        '*.txt'), ('All files', '*.*')])
       
    # get input file
    root = tkinter.Tk()  # where to open
    root.withdraw()  # hide Frame
    edi_path = fd.askopenfilename(**FILEOPENOPTIONS)  # choose a file
    
    if(edi_path is None or edi_path == ""): # if the file picker closed
        exit("No file chosen")  # shutdown before log is written

# create and open the log file for this session

file = open(path + '\\logs\\EDILog' + time + '.txt', 'w+')  
file.write("starting EDI check at " + time + '\n')  # write to log
file.write("using EDI: " + edi_path + '\n')
print("using EDI: " + edi_path + '\n')

with open(edi_path, 'r') as edif:
    content = edif.readlines()
    
SIZE = len(content)

file.write("There are " + str(SIZE) + " lines in the EDI\n")    

cntr = 1
errors = 0
for line in content:
    if( cntr == SIZE):
        if len(line) in (2000, 2001):
            print("trailer : " + str(len(line)))
            file.write("trailer : " + str(len(line)))
        else:
            print("trailer Error: " + str(len(line)))
            file.write("trailer Error: " + str(len(line)))
            errors += 1
            
        cntr += 1
        continue
    elif len(line) != 2001:
        print("Line " + str(cntr) + " Error, chars: " + str(len(line)))
        file.write("Line " + str(cntr) + " Error, chars: " + str(len(line)) + '\n')
        cntr += 1
        errors += 1
    else:
        #print("Line " + str(cntr) + " OK, chars: " + str(len(line)))
        file.write("Line " + str(cntr) + " chars: " + str(len(line)))
        cntr += 1

if not content[0].startswith('H'):
    errors += 1
    print("Header does not start with H")
    file.write("Header does not start with H\n")
        
if not content[SIZE-1].startswith('T'):
    errors += 1
    print("Trailer does not start with T")
    file.write("Trailer does not start with T\n")
else:
    tList = content[SIZE-1].split()
    if(int(tList[0].replace('T','')) != SIZE-2):
        print('Trailer record size is ' + tList[0].replace('T','') + 
            ' but should be ' + str(SIZE-2))
        errors += 1
        
header = content[0]

if not checkNum(header, 61, 69):
    print('failed converting group number to int: ' + header[61:69])
    file.write('failed converting group number to int: ' + header[61:69] + '\n')
    errors += 1 

if header[69:84].strip() != "33-0783173":
    print('Send ID is incorrect: ' + header[69:84] + " should be 33-0783173")
    file.write('Send ID is incorrect: ' + header[69:84] + 
        " should be 33-0783173\n")
    errors += 1
    
if not checkDate(header, 84, 92):
    print('File date is incorrect: ' + header[84:92] + " is not a valid date")
    file.write('File date is incorrect: ' + header[84:92] + 
        " is not a valid date\n")
    errors += 1

try:
    int(header[94:98])
except ValueError:
    print('File time is incorrect: ' + header[94:98] + " is not a valid time")
    file.write('File time is incorrect: ' + header[94:98] + 
        " is not a valid time\n")
    errors += 1

if header[102] not in ('P', 'T'):
    print('File type is incorrect: ' + header[102] + " is not T or P")
    file.write('File date is incorrect: ' + header[102] + " is not T or P\n")
    errors += 1
    
if header[103] not in('F','C'):
    print('Usage type is incorrect: ' + header[103] + " is not F or C")
    file.write('Usage type is incorrect: ' + header[103] + " is not F or C\n")
    errors += 1
    
tail = header[len(header)-1]
if(tail != '\n'):
    print("Header doesn't end with a line break")
    file.write("Header doesn't end with a line break\n")
    errors += 1
    
cntr = 1
trailNum = SIZE
for line in content:
    if cntr == 1:
        cntr +=1
        continue
    
    if cntr == trailNum:
        break
    
    SIZE = len(line)
    
    if line[0] != 'D':
        print("line " + str(cntr) + " doesn't start with D")
        file.write("line " + str(cntr) + " doesn't start with D\n")
        errors += 1
    
    if line[1] not in ('D', 'E'):
        print("line " + str(cntr) + " doesn't start with D or E")
        file.write("line " + str(cntr) + " doesn't start with D or E\n")
        errors += 1
    
    SSN = line[2:13].strip()
    try:
        if SSN != "":
            int(SSN.replace("-","").strip())
    except ValueError:
            print('line ' + str(cntr) + ' SSN ' + SSN + " is not a valid SSN")
            file.write('line ' + str(cntr) + ' SSN ' + SSN + 
                " is not a valid SSN\n")
            errors += 1
            
    if SSN != "":        
        if SSN[3] != '-' or SSN[6] != '-':
            print('line ' + str(cntr) + ' SSN ' + SSN + 
                " is not a valid SSN format")
            file.write('line ' + str(cntr) + ' SSN ' + SSN + 
                " is not a valid SSN format\n")
            errors += 1
        
    if line[21:23] not in ('FT', 'RT', '  '):
        print('line ' + str(cntr) + " \"" + line[21:23] + 
            "\" is not a valid Employment Status")
        file.write('line ' + str(cntr) + " \"" + line[21:23] + 
            "\" is not a valid Employment Status\n")
        errors += 1
    
    if line[26:30] not in ('0000','0001','0002','0003'):
        print('line ' + str(cntr) + " \"" + line[26:30] + 
            "\" is not a valid class code")
        file.write('line ' + str(cntr) + " \"" + line[26:30] + 
            "\" is not a valid class code\n")
        errors += 1
    
    if not checkDate(line, 30, 40):
        print('line ' + str(cntr) + " \"" + line[30:40] + 
            "\" is not a valid Class Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[30:40] + 
            "\" is not a valid Class Effective Date\n")
        errors += 1
    
    if not checkNum(line, 40, 44):
        print('line ' + str(cntr) + " \"" + line[40:44] + 
            "\" is not a valid Division Code")
        file.write('line ' + str(cntr) + " \"" + line[40:44] + 
            "\" is not a valid Division Code\n")
        errors += 1
    
    if not checkDate(line, 44, 54):
        print('line ' + str(cntr) + " \"" + line[44:54] + 
            "\" is not a valid Division Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[44:54] + 
            "\" is not a valid Division Effective Date\n")
        errors += 1
    
    if not checkDate(line, 62, 72):
        print('line ' + str(cntr) + " \"" + line[62:72] + 
            "\" is not a valid hire date")
        file.write('line ' + str(cntr) + " \"" + line[62:72] + 
            "\" is not a valid hire date\n")
        errors += 1
    
    if not checkDate(line, 72, 82):
        print('line ' + str(cntr) + " \"" + line[72:82].strip() + 
            "\" is not a valid retire date")
        file.write('line ' + str(cntr) + " \"" + line[72:82].strip() + 
            "\" is not a valid retire date\n")
        errors += 1
    
    if not checkDate(line, 82, 92):
        print('line ' + str(cntr) + " \"" + line[82:92].strip() + 
            "\" is not a valid termination date")
        file.write('line ' + str(cntr) + " \"" + line[82:92].strip() + 
            "\" is not a valid termination date\n")
        errors += 1
        
    if not checkPhone(line, 154, 166):
        print('line ' + str(cntr) + " \"" + line[154:166] + 
            "\" is not a valid Home Phone")
        file.write('line ' + str(cntr) + " \"" + line[154:166] + 
            "\" is not a valid Home Phone\n")
        errors += 1
    
    atCntr = 0
    emailAddr = line[166:216].strip()
    if emailAddr != "":
        for x in emailAddr:
            if x == '@':
                atCntr += 1
        
        if atCntr != 1 or '.' not in emailAddr:
            print('line ' + str(cntr) + " \"" + emailAddr + 
                "\" is not a valid Email Address")
            file.write('line ' + str(cntr) + " \"" + emailAddr + 
                "\" is not a valid Email Address\n")
            errors += 1
        
    if line[306:308] not in('CA', "  "):
        print('line ' + str(cntr) + " \"" + line[306:308] + 
            "\" is not a valid State")
        file.write('line ' + str(cntr) + " \"" + line[306:308] + 
            "\" is not a valid State\n")
        errors += 1
        
    if not checkDate(line, 320, 330):
        print('line ' + str(cntr) + " \"" + line[320:330] + 
            "\" is not a valid termination date")
        file.write('line ' + str(cntr) + " \"" + line[320:330] + 
            "\" is not a valid termination date\n")
        errors += 1
        
    if line[330] not in ('F', 'M', ''):
        print('line ' + str(cntr) + " \"" + line[330] + 
            "\" is not a valid gender")
        file.write('line ' + str(cntr) + " \"" + line[330] + 
            "\" is not a gender\n")
        errors += 1        
    
    if line[331:333] not in ('SP','CH','AC','FC','DP','CA','SC','EX','SE'):
        print('line ' + str(cntr) + " \"" + line[320:330] + 
            "\" is not a valid RELATIONSHIP CODE")
        file.write('line ' + str(cntr) + " \"" + line[320:330] + 
            "\" is not a RELATIONSHIP CODE\n")
        errors += 1
    
    if not checkDate(line, 320, 330):
        print('line ' + str(cntr) + " \"" + line[320:330] + 
            "\" is not a valid DOB")
        file.write('line ' + str(cntr) + " \"" + line[320:330] + 
            "\" is not a DOB\n")
        errors += 1
        
    if line[333:334] not in ('M','S','U','W', 'D', ' '):
        print('line ' + str(cntr) + " \"" + line[333:334] + 
            "\" is not a valid marital status")
        file.write('line ' + str(cntr) + " \"" + line[333:334] + 
            "\" is not a marital status\n")
        errors += 1
    
    SSN = line[334:345].strip()
    try:
        if SSN != "":
            int(SSN.replace("-","").strip())
    except ValueError:
            print('line ' + str(cntr) + ' SSN ' + SSN + 
                " is not a valid dependent SSN")
            file.write('line ' + str(cntr) + ' SSN ' + SSN + 
                " is not a valid dependent SSN\n")
            errors += 1
            
    if SSN != "" and (SSN[3] != '-' or SSN[6] != '-'):
        print('line ' + str(cntr) + ' SSN ' + SSN + 
            " is not a valid dependent SSN format")
        file.write('line ' + str(cntr) + ' SSN ' + SSN + 
            " is not a valid dependent SSN format\n")
        errors += 1
    
    if line[345:346] not in ('F', 'N', ' '):
        print('line ' + str(cntr) + " \"" + line[345:346] + 
            "\" is not a valid student status")
        file.write('line ' + str(cntr) + " \"" + line[345:346] + 
            "\" is not a valid student status\n")
        errors += 1
    
    if line[346:347] not in ('H', ' '):
        print('line ' + str(cntr) + " \"" + line[346:347] + 
            "\" is not a valid student status")
        file.write('line ' + str(cntr) + " \"" + line[346:347] + 
            "\" is not a valid student status\n")
        errors += 1
    
    if not checkNum(line, 347, 364):
        print('line ' + str(cntr) + " \"" + line[347:364] + 
            "\" is not a valid salary")
        file.write('line ' + str(cntr) + " \"" + line[347:364] + 
            "\" is not a valid salary\n")
        errors += 1
    
    if line[364:366].strip() not in ('H', 'W', 'BI', 'SM', 'M', 'A', ""):
        print('line ' + str(cntr) + " \"" + line[347:364] + 
            "\" is not a valid salary type")
        file.write('line ' + str(cntr) + " \"" + line[347:364] + 
            "\" is not a valid salary type\n")
        errors += 1
    
    if not checkDate(line, 366, 376):
        print('line ' + str(cntr) + " \"" + line[366:376] + 
            "\" is not a valid salary effective date")
        file.write('line ' + str(cntr) + " \"" + line[366:376] + 
            "\" is not a valid salary effective date\n")
        errors += 1
    
    if not checkNum(line, 376, 380):
        print('line ' + str(cntr) + " \"" + line[376:380] + 
            "\" is not a valid hours worked")
        file.write('line ' + str(cntr) + " \"" + line[376:380] + 
            "\" is not a valid hours worked\n")
        errors += 1
    
    if line[380] not in ('T', 'N', ' '):
        print('line ' + str(cntr) + " \"" + line[380] + 
            "\" is not a valid smoker code")
        file.write('line ' + str(cntr) + " \"" + line[380] + 
            "\" is not a valid smoker code\n")
        errors += 1

    # END BIOGRAPHICAL DATA CHECK*********************************# 
    
    # START STD CHECKS********************************************# 
    
    if line[613:623].strip() not in ('STD', ''):
        print('line ' + str(cntr) + " \"" + line[613:623] + 
            "\" is not a valid STD Coverage Election code")
        file.write('line ' + str(cntr) + " \"" + line[613:623] + 
            "\" is not a valid STD Coverage Election Code\n")
        errors += 1
        
    if line[646:649].strip() not in ("EMP", ""):
        print('line ' + str(cntr) + " \"" + line[646:649] + 
            "\" is not a valid STD Coverage Level")
        file.write('line ' + str(cntr) + " \"" + line[646:649] + 
            "\" is not a valid STD Coverage Level\n")
        errors += 1
    
    if not checkDate(line, 649,659):
        print('line ' + str(cntr) + " \"" + line[649:659] + 
            "\" is not a valid STD Coverage Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[649:659] + 
            "\" is not a valid STD Coverage Effective Date\n")
        errors += 1
        
    if not checkDate(line, 659, 669):
        print('line ' + str(cntr) + " \"" + line[659:669] + 
            "\" is not a valid STD Coverage End Date")
        file.write('line ' + str(cntr) + " \"" + line[659:669] + 
            "\" is not a valid STD Coverage End Date\n")
        errors += 1
    
    # END STD CHECKS***********************************************# 
    
    # START Basic Life CHECKS**************************************# 
    
    if line[669:679].strip() not in ('LIFE', ''):
        print('line ' + str(cntr) + " \"" + line[669:679] + 
            "\" is not a valid Basic Life Coverage Election code")
        file.write('line ' + str(cntr) + " \"" + line[669:679] + 
            "\" is not a valid Basic Life Coverage Election Code\n")
        errors += 1
        
    if line[702:705].strip() not in ("EMP", ""):
        print('line ' + str(cntr) + " \"" + line[702:705] + 
            "\" is not a valid Basic Life Coverage Level")
        file.write('line ' + str(cntr) + " \"" + line[702:705] + 
            "\" is not a valid Basic Life Coverage Level\n")
        errors += 1
    
    if not checkDate(line, 705,715):
        print('line ' + str(cntr) + " \"" + line[705:715] + 
            "\" is not a valid Basic Life Coverage Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[705:715] + 
            "\" is not a valid Basic Life Coverage Effective Date\n")
        errors += 1
        
    if not checkDate(line, 715, 725):
        print('line ' + str(cntr) + " \"" + line[715:725] + 
            "\" is not a valid Basic Life Coverage End Date")
        file.write('line ' + str(cntr) + " \"" + line[715:725] + 
            "\" is not a valid Basic Life Coverage End Date\n")
        errors += 1
# END BASIC LIFE CHECKS***********************************************# 
 
# START AD&D CHECKS**************************************************# 
    
    if line[725:735].strip() not in ('ADD', ''):
        print('line ' + str(cntr) + " \"" + line[725:735] + 
            "\" is not a valid AD&D Coverage Election code")
        file.write('line ' + str(cntr) + " \"" + line[725:735] + 
            "\" is not a valid AD&D Coverage Election Code\n")
        errors += 1
        
    if line[758:761].strip() not in ("EMP", ""):
        print('line ' + str(cntr) + " \"" + line[758:761] + 
            "\" is not a valid AD&D Coverage Level")
        file.write('line ' + str(cntr) + " \"" + line[758:761] + 
            "\" is not a valid AD&D Coverage Level\n")
        errors += 1
    
    if not checkDate(line, 761,771):
        print('line ' + str(cntr) + " \"" + line[761:771] + 
            "\" is not a valid AD&D Coverage Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[761:771] + 
            "\" is not a valid AD&D Coverage Effective Date\n")
        errors += 1
        
    if not checkDate(line, 771, 781):
        print('line ' + str(cntr) + " \"" + line[771:781] + 
            "\" is not a valid AD&D Coverage End Date")
        file.write('line ' + str(cntr) + " \"" + line[771:781] + 
            "\" is not a valid AD&D Coverage End Date\n")
        errors += 1
    # END AD&D CHECKS****************************************************# 
   
    # START Vol Life CHECKS**************************************************# 
    
    if line[837:847].strip() not in ('VOLLIF', ''):
        print('line ' + str(cntr) + " \"" + line[837:847] + 
            "\" is not a valid Vol Life Coverage Election code")
        file.write('line ' + str(cntr) + " \"" + line[837:847] + 
            "\" is not a valid Vol Life Coverage Election Code\n")
        errors += 1
        
    if line[870:873].strip() not in ("EMP",'ESP','ECH','FAM',
        'SPO','CHD','SPC', ""):
        print('line ' + str(cntr) + " \"" + line[870:873] + 
            "\" is not a valid Vol Life Coverage Level")
        file.write('line ' + str(cntr) + " \"" + line[870:873] + 
            "\" is not a valid Vol Life Coverage Level\n")
        errors += 1
    
    if not checkNum(line, 855, 870):
        print('line ' + str(cntr) + " \"" + line[855:870] + 
            "\" is not a valid Vol Life Volume Election")
        file.write('line ' + str(cntr) + " \"" + line[855:870] + 
            "\" is not a valid Vol Life Volume Election\n")
        errors += 1

    if not checkDate(line, 873,883):
        print('line ' + str(cntr) + " \"" + line[873,883] + 
            "\" is not a valid Vol Life Coverage Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[873,883] + 
            "\" is not a valid Vol Life Coverage Effective Date\n")
        errors += 1
        
    if not checkDate(line, 883, 893):
        print('line ' + str(cntr) + " \"" + line[883:893] + 
            "\" is not a valid Vol Life Coverage End Date")
        file.write('line ' + str(cntr) + " \"" + line[883:893] + 
            "\" is not a valid Vol Life Coverage End Date\n")
        errors += 1

    # END Vol Life CHECKS****************************************************# 

    # START Vol AD&D CHECKS**************************************************# 
    
    if line[893:903].strip() not in ('VOLADD', ''):
        print('line ' + str(cntr) + " \"" + line[893:903] + 
            "\" is not a valid Vol AD&D Coverage Election code")
        file.write('line ' + str(cntr) + " \"" + line[893:903] + 
            "\" is not a valid Vol AD&D Coverage Election Code\n")
        errors += 1

    if not checkNum(line, 911, 926):
        print('line ' + str(cntr) + " \"" + line[855:870] + 
            "\" is not a valid Vol AD&D Volume Election")
        file.write('line ' + str(cntr) + " \"" + line[855:870] + 
            "\" is not a valid Vol AD&D Volume Election\n")
        errors += 1
        
    if line[926:929].strip() not in ("EMP",'ESP','ECH','FAM',
        'SPO','CHD','SPC', ""):
        print('line ' + str(cntr) + " \"" + line[926:929] + 
            "\" is not a valid Vol AD&D Coverage Level")
        file.write('line ' + str(cntr) + " \"" + line[926:929] + 
            "\" is not a valid Vol AD&D Coverage Level\n")
        errors += 1

    if not checkDate(line, 929,939):
        print('line ' + str(cntr) + " \"" + line[929,939] + 
            "\" is not a valid Vol AD&D Coverage Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[929,939] + 
            "\" is not a valid Vol AD&D Coverage Effective Date\n")
        errors += 1
        
    if not checkDate(line, 939, 949):
        print('line ' + str(cntr) + " \"" + line[939:949] + 
            "\" is not a valid Vol AD&D Coverage End Date")
        file.write('line ' + str(cntr) + " \"" + line[939:949] + 
            "\" is not a valid Vol AD&D Coverage End Date\n")
        errors += 1

    # END Vol AD&D CHECKS****************************************************# 
    
    # START VOL LTD CHECKS**************************************************# 
    
    if line[949:959].strip() not in ('VOLLTD', ''):
        print('line ' + str(cntr) + " \"" + line[949:959] + 
            "\" is not a valid LTD Coverage Election code")
        file.write('line ' + str(cntr) + " \"" + line[949:959] + 
            "\" is not a valid LTD Coverage Election Code\n")
        errors += 1
        
    if line[982:985].strip() not in ("EMP", ""):
        print('line ' + str(cntr) + " \"" + line[982:985] + 
            "\" is not a valid LTD Coverage Level")
        file.write('line ' + str(cntr) + " \"" + line[982:985] + 
            "\" is not a valid LTD Coverage Level\n")
        errors += 1
    
    if not checkDate(line, 985,995):
        print('line ' + str(cntr) + " \"" + line[985:995] + 
            "\" is not a valid LTD Coverage Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[985:995] + 
            "\" is not a valid LTD Coverage Effective Date\n")
        errors += 1
        
    if not checkDate(line, 995, 1005):
        print('line ' + str(cntr) + " \"" + line[995:1005] + 
            "\" is not a valid LTD Coverage End Date")
        file.write('line ' + str(cntr) + " \"" + line[995:1005] + 
            "\" is not a valid LTD Coverage End Date\n")
        errors += 1
    # END VOL LTD CHECKS****************************************************# 

    # START CANCER CHECKS**************************************************# 
    
    if line[1158:1168].strip() not in ('CAN', ''):
        print('line ' + str(cntr) + " \"" + line[1158:1168] + 
            "\" is not a valid CANCER Coverage Election code")
        file.write('line ' + str(cntr) + " \"" + line[1158:1168] + 
            "\" is not a valid CANCER Coverage Election Code\n")
        errors += 1
        
    if line[1176:1179].strip() not in ("EMP",'ESP','ECH','FAM',
        'SPO','CHD','SPC', ""):
        print('line ' + str(cntr) + " \"" + line[1176:1179] + 
            "\" is not a valid CANCER Coverage Level")
        file.write('line ' + str(cntr) + " \"" + line[1176:1179] + 
            "\" is not a valid CANCER Coverage Level\n")
        errors += 1
    
    if not checkDate(line, 1179,1189):
        print('line ' + str(cntr) + " \"" + line[1179:1189] + 
            "\" is not a valid CANCER Coverage Effective Date")
        file.write('line ' + str(cntr) + " \"" + line[1179:1189] + 
            "\" is not a valid LTD Coverage Effective Date\n")
        errors += 1
        
    if not checkDate(line, 1189, 1199):
        print('line ' + str(cntr) + " \"" + line[1189:1199] + 
            "\" is not a valid CANCER Coverage End Date")
        file.write('line ' + str(cntr) + " \"" + line[1189:1199] + 
            "\" is not a valid CANCER Coverage End Date\n")
        errors += 1
    # END CANCER CHECKS****************************************************# 

    cntr += 1
print("Scan completed, there are " + str(errors) + " errors in the file")
file.close()
input("Press Enter to continue")