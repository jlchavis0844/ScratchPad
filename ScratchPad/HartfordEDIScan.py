'''
This script will eventually do some error checking on a
completed Hartford EDI file. For now (8/24/2017), I will
focus on just removing empty sections and renaming the
file extensions

10/10/2017 - removed the function of checking for and removing empty sections.
             Empty sections will now left in
10/10/2017 - Commented out sections to create another EDI file with removed sections.
'''
import datetime, json, requests, sys, os, csv, ctypes, re
import tkinter  # for the file picker
import tkinter.filedialog as fd  # for picking the file
from datetime import datetime
from dateutil.parser import parse
from win32verstamp import stamp
from win32api import BeginUpdateResource

'''
A simple function that returns whether the given substring can be 
converted into a valid integer
This method uses simple try/catch on conversion
@param line - String of the text we will be taking the substring 
from
@return boolean on whether the substring can be converted 
'''
def checkNum(line):
    try:
        if line.strip() != "":
            int(line.strip())
        return True
    except ValueError:
        return False
    

'''
A function that attempts to convert a substring into a date in 
the format of YYYYMMDD.Failure means that it is not a proper date,
relies on datetime.datetime.strptime
@param line - string of the text we will be taking the substring 
from
@return boolean on whether the substring can be converted 
'''
def checkDate(line):
    try:
        if line.strip() != "":
            datetime.strptime(line.strip(),'%Y%m%d')
        return True
    except ValueError:
        return False

'''A function to check the validity of a time stamp
@param line - the candidate time stamp
@return boolean false is exception on parse is raised, else true
'''
def checkTimeStamp(line):
    try:
        dt = parse(line)
        return True
    except ValueError:
        return False

'''
Runs basic checks on PII section. Checks for presence and date and SSN validity
'''   
def checkPII(tokens):
    global errors
    global file
    #tokens[0] is section header, should be blank
    if tokens[1] != "1225486":
        file.write('ERROR: Customer number found: ' + tokens[1] + '\n')
        print('ERROR: Customer number found: ' + tokens[1] + '\n')
        errors += 1
        
    if tokens[2] not in ['D', 'E']:
        file.write('ERROR: Transaction Code not valid: ' + tokens[2] + '\n')
        print('ERROR: Transaction Code not valid: ' + tokens[2] + '\n')
        errors+=1
        
    if tokens[2] == 'E':
        dependent == False        
        
    if checkNum(tokens[3]) == False or len(tokens[3].strip()) != 9 or tokens[3] is None:
        file.write('ERROR: Employee SSN not valid: ' + tokens[3] + '\n')        
        print('ERROR: Employee SSN not valid: ' + tokens[3] + '\n')
        errors+=1
    
    #tokens[4] is employee ID, check only for entry, throw warning, not error.
    if tokens[4] == '' or tokens[4] is None:
        file.write('Warning: Employee ID is empty')
        print('Warning: Employee ID is empty')
    
    if checkNum(tokens[5]) == False or len(tokens[5].strip()) != 9 or tokens[3] is None:
        file.write('Warning: member SSN not valid: ' + tokens[5] + '\n')
        #print('Warning: member SSN not valid: ' + tokens[5] + '\n')
        #errors+=1
    
    if tokens[6] not in rcodes:
        file.write('ERROR: Invalid Relationship Code: ' + tokens[6] + '\n')
        print('ERROR: Invalid Relationship Code: ' + tokens[6] + '\n')
        errors+=1
        
    if tokens[7] is None or tokens[7].strip() == '':
        file.write('ERROR: Invalid Last Name: ' + tokens[7] + '\n')
        print('ERROR: Invalid Last Name: ' + tokens[7] + '\n')
        errors+=1
    
    if tokens[8] is None or tokens[8].strip() == '':
        file.write('ERROR: Invalid First Name: ' + tokens[8] + '\n')
        print('ERROR: Invalid First Name: ' + tokens[8] + '\n')
        errors+=1
    
    if len(tokens[9]) > 1:
        file.write('ERROR: Invalid middle initial: ' + tokens[9] + '\n')
        print('ERROR: Invalid middle initial: ' + tokens[9] + '\n')
        errors+=1
    
    #skip tokens[10] and tokens[11] prefix and suffix
    
    if tokens[12] is None or tokens[12].strip() == '' or checkDate(tokens[12]) == False:
        file.write('ERROR: Invalid Birth Date: ' + tokens[12] + '\n')
        print('ERROR: Invalid Birth Date: ' + tokens[12] + '\n')
        errors+=1
    
    if tokens[13] is None or tokens[13].strip() == '' or tokens[13] not in mcodes:
        file.write('WARNING: Invalid Marriage Status: ' + tokens[13] + '\n')
        print('WARNING: Invalid Marriage Status: ' + tokens[13] + '\n')
    
    if tokens[14] is None or tokens[14].strip() == '' or tokens[14] not in ['M', 'F','U']:
        file.write('ERROR: Invalid Gender: ' + tokens[14] + '\n')
        print('ERROR: Invalid Gender: ' + tokens[14] + '\n')
        errors+=1
    
    if tokens[15] is None or tokens[15].strip() == '':
        file.write('WARNING: Missing Smoker status\n')
        print('WARNING: Missing Smoker status\n')
        
'''
Runs check on HDR Section
'''        
def checkHDR(tokens):
    global errors
    global file
    global edi_path
    
    if len(tokens[0]) != 0:
        file.write("WARNING, Section code is not empty\n")
        print("WARNING, Section code is not empty\n")
    
    if tokens[1] != '1':
        file.write('ERROR: Customer count is not 1\n')
        print('ERROR: Customer count is not 1\n')
        errors +=1
        
    if tokens[2] not in edi_path:
        file.write("ERROR, The file name doesn't match loaded EDI file\n")
        file.write("Actual file loaded: " + edi_path + '\n')
        file.write('File name in header: ' + tokens[2] + '\n')
        print("ERROR, The file name doesn't match loaded EDI file\n")
        print("Actual file loaded: " + edi_path + '\n')
        print('File name in header: ' + tokens[2] + '\n')
        errors+=1
        
    if len(tokens[3]) == 0 or checkTimeStamp(tokens[3]) == False:
        file.write('ERROR: Invalid time stamp ' + tokens[3] + '\n')
        print('ERROR: Invalid time stamp ' + tokens[3] + '\n')
        errors +=1
        
    if len(tokens[4]) < 1:
        file.write('ERROR, missing customer name\n')
        print('Error, missing customer name\n')
        errors +=1
    
    if len(tokens[5]) < 1:
        file.write('ERROR, missing file version\n')
        print('Error, missing file version\n')
        errors +=1


def checkECI(tokens):
    global file
    global errors
    
    if len(tokens[0]) != 0:
        file.write("WARNING, Section code is not empty\n")
        print("WARNING, Section code is not empty\n")
        
    #tokens 1.2.3.5.7.8,11,12,14-20 are address with nothing to check
    
    if len(tokens[5]) != 0 and checkNum(tokens[5]) == False and len(tokens[5]) != 5:
        file.write('ERROR: Invalid Address Zip: ' + tokens[5] + '\n')
        print('ERROR: Invalid Address Zip: ' + tokens[5] + '\n')
        errors+=1
                
    if tokens[6] != '840':
        file.write('ERROR: Invalid country code: ' + tokens[6] + '\n')
        print('ERROR: Invalid country code: ' + tokens[6] + '\n')
        errors+=1

    if len(tokens[9]) != 0:#s'ok if it be null
        if len(tokens[9]) != 10 or checkNum(tokens[9]) == False:
            file.write('ERROR: Invalid Home Phone: ' + tokens[9] + '\n')
            print('ERROR: Invalid Home Phone: ' + tokens[9] + '\n')
            errors+=1

    if len(tokens[10]) != 0:
        if len(tokens[10]) != 9 or checkNum(tokens[10]) == False:
            file.write('ERROR: Invalid Cell Phone: ' + tokens[10] + '\n')
            print('ERROR: Invalid C Phone: ' + tokens[10] + '\n')
            errors+=1
            
    if tokens[13] != 'CA':
        file.write('ERROR: Invalid state code: ' + tokens[13] + '\n')
        print('ERROR: Invalid state code: ' + tokens[13] + '\n')
        errors+=1

def checkEMI(tokens):
    global file
    global errors
    
    if len(tokens[0]) != 0:
        file.write("WARNING, Section code for EMI is not empty\n")
        print("WARNING, Section code EMI is not empty\n")  
        
    if len(tokens[1]) != 1 or tokens[1] not in statcodes:
        file.write('ERROR: Invalid status code: ' + tokens[2] + '\n')
        print('ERROR: Invalid status code: ' + tokens[2] + '\n')
        errors+=1

    if len(tokens[2]) != 0 and checkDate(tokens[2]) == False:
        file.write('ERROR: Invalid Status Effective Date: ' + tokens[2] + '\n')
        print('ERROR: Invalid Status Effective Date: ' + tokens[2] + '\n')
        errors+=1
        
    if len(tokens[3]) != 0 and checkDate(tokens[3]) == False:
        file.write('ERROR: Invalid Employee Service Date: ' + tokens[3] + '\n')
        print('ERROR: Invalid Employee Service Date: ' + tokens[3] + '\n')
        errors+=1
        
    if len(tokens[4]) != 0 and checkDate(tokens[4]) == False:
        file.write('ERROR: Invalid Employee Rehire Date: ' + tokens[4] + '\n')
        print('ERROR: Invalid Employee Rehire Date: ' + tokens[4] + '\n')
        errors+=1
        
    if len(tokens[5]) != 0 and checkDate(tokens[5]) == False:
        file.write('ERROR: Invalid Employee Original Rehire Date: ' + tokens[5] + '\n')
        print('ERROR: Invalid Employee Original Rehire Date: ' + tokens[5] + '\n')
        errors+=1

    #tokens[7-8] term details
    
    if tokens[9] not in ['F', 'P']:
        file.write('ERROR: Invalid Employment type: ' + tokens[9] + '\n')
        print('ERROR: Invalid Employment type: ' + tokens[9] + '\n')
        errors+=1
    
    if tokens[10] not in ['E', 'N']:
        file.write('ERROR: Invalid Employment type: ' + tokens[10] + '\n')
        print('ERROR: Invalid Employment type: ' + tokens[10] + '\n')
        errors+=1
        
    if len(tokens[11]) != 0:
        file.write('ERROR: Scheduled Hours Per Week not null: ' + tokens[11] + '\n')
        print('ERROR: Scheduled Hours Per Week not null: ' + tokens[11] + '\n')
        errors+=1
        
    if len(tokens[12]) == 0 or checkNum(tokens[12]) == False:
        file.write('ERROR: Benefit Salary Amount: ' + tokens[12] + '\n')
        print('ERROR: Benefit Salary Amount: ' + tokens[12] + '\n')
        errors+=1
        
    if tokens[13] not in ['A', 'W', 'M', 'B', 'S']:
        file.write('ERROR: Salary Basis: ' + tokens[13] + '\n')
        print('ERROR: Salary Basis: ' + tokens[13] + '\n')
        errors+=1
        
    if len(tokens[14]) == 0 or checkDate(tokens[14]) == False:
        file.write('ERROR: Salary Effective Date: ' + tokens[14] + '\n')
        print('ERROR: Salary Effective Date: ' + tokens[14] + '\n')
        errors+=1
        
    if len(tokens[17]) == 0:
        file.write('WARNING: Missing job title\n')
        print('WARNING: Missing job title\n')
        
    
def checkNST(tokens):
    global file
    global errors
    
    if len(tokens[0]) != 0:
        file.write("WARNING, Section code is not null\n") 
        print("WARNING, Section code is not null\n") 
        
    if len(tokens[1]) != 0 and checkDate(tokens[1]) == False:
        file.write("WARNING, invalid NST Coverage Effective Date\n" + tokens[1] + '\n') 
        print("WARNING, invalid NST Coverage Effective Date\n" + tokens[1] + '\n') 
    
    if len(tokens[2]) != 0 and checkDate(tokens[2]) == False:
        file.write("WARNING, invalid NST Coverage Termination Date\n" + tokens[2] + '\n') 
        print("WARNING, invalid NST Coverage Termination Date\n" + tokens[2] + '\n') 
        
    if len(tokens[3]) != 0:
        file.write("WARNING, Covered Salary  is not null\n") 
        print("WARNING, Covered Salary  is not null\n") 
        
    if len(tokens[4]) != 0 and tokens[4] != "60":
        file.write("WARNING, invalid Coverage Plan Option\n" + tokens[2] + '\n') 
        print("WARNING, invalid Coverage Plan Option\n" + tokens[2] + '\n') 
        
    if len(tokens[5]) != 0:
        file.write("WARNING, Requested Coverage Plan Option is not null\n") 
        print("WARNING, Requested Coverage Plan Option is not null\n")     
        
    if len(tokens[6]) != 0:
        file.write("WARNING, Employee Group ID is not null\n") 
        print("WARNING, Employee Group ID is not null\n")
        
    if len(tokens[7]) != 0:
        file.write("WARNING, Employee Class Code is not null\n") 
        print("WARNING, Employee Class Code is not null\n")
        

def checkLTD(tokens):
    global file
    global errors
    
    if len(tokens[0]) != 0:
        file.write("WARNING, Section code is not null\n") 
        print("WARNING, Section code is not null\n") 
        
    if len(tokens[1]) != 0 and checkDate(tokens[1]) == False:
        file.write("WARNING, invalid LTD Coverage Effective Date\n" + tokens[1] + '\n') 
        print("WARNING, invalid LTD Coverage Effective Date\n" + tokens[1] + '\n') 
    
    if len(tokens[2]) != 0 and checkDate(tokens[2]) == False:
        file.write("WARNING, invalid LTD Coverage Termination Date\n" + tokens[2] + '\n') 
        print("WARNING, invalid LTD Coverage Termination Date\n" + tokens[2] + '\n') 
        
    if len(tokens[3]) != 0:
        file.write("WARNING, Coverage Termination Reason Code is not null\n") 
        print("WARNING, Coverage Termination Reason Code is not null\n") 
        
    if len(tokens[4]) != 0:
        file.write("WARNING, Coverage Termination Description is not null\n") 
        print("WARNING, Coverage Termination Description is not null\n")
        
    if len(tokens[5]) != 0:
        file.write("WARNING, LTD Covered Salary is not null\n") 
        print("WARNING, LTD Covered Salary is not null\n")     
        
    if len(tokens[6]) != 0 and tokens[6] != "60":
        file.write("WARNING, invalid Coverage Plan Option\n" + tokens[2] + '\n') 
        print("WARNING, invalid Coverage Plan Option\n" + tokens[2] + '\n') 
        
    if len(tokens[7]) != 0:
        file.write("WARNING, Requested Coverage Plan Option is not null\n") 
        print("WARNING, Requested Coverage Plan Option is not null\n")       
        
    if len(tokens[8]) != 0:
        file.write("WARNING, Employee Group ID is not null\n") 
        print("WARNING, Employee Group ID is not null\n")   
        
    if len(tokens[9]) != 0:
        file.write("WARNING, Employee Class Code is not null\n") 
        print("WARNING, Employee Class Code is not null\n")  
        
        
        
def checkVCI(tokens):
    global file
    global errors
    
    if len(tokens[0]) != 0:
        file.write("WARNING, Section code is not null for VCI\n") 
        print("WARNING, Section code is not null for VCI\n")

    if len(tokens[1]) != 0 and checkDate(tokens[1]) == False:
        file.write("WARNING, invalid VCI Coverage Effective Date\n" + tokens[1] + '\n') 
        print("WARNING, invalid VCI Coverage Effective Date\n" + tokens[1] + '\n') 
        
    if len(tokens[2]) != 0 and checkDate(tokens[2]) == False:
        file.write("WARNING, VCI Coverage Termination Description is not null\n") 
        print("WARNING, VCI Coverage Termination Description is not null\n")    
        
    if len(tokens[3]) != 0:
        file.write("WARNING, VCI Coverage Termination Reason Code is not null\n") 
        print("WARNING, VCI Coverage Termination Reason Code is not null\n") 
        
    if len(tokens[4]) != 0:
        file.write("WARNING, VCI Coverage Termination Description is not null\n") 
        print("WARNING, VCI Coverage Termination Description is not null\n")
        
    if len(tokens[5]) != 0 and tokens[5] not in ['5000', '10000', '20000']:
        file.write("WARNING, invalid VCI CI Benefit Amount\n" + tokens[5] + '\n') 
        print("WARNING, invalid VCI CI Benefit Amount\n" + tokens[5] + '\n')
        
    if len(tokens[6]) != 0 and tokens[6] not in ['1', '2', '3', '4', '5']:
        file.write("WARNING, invalid VCI CI Benefit Amount\n" + tokens[5] + '\n') 
        print("WARNING, invalid VCI CI Benefit Amount\n" + tokens[5] + '\n')
    
    if len(tokens[7]) != 0 and tokens[7] != '001': #changed from 1225486 to 001 for CI & ACC
        file.write("WARNING, invalid VCI Plan Number\n" + tokens[5] + '\n') 
        print("WARNING, invalid VCI Plan Number\n" + tokens[5] + '\n')
    
    if len(tokens[8]) != 0:
        file.write("WARNING, Employee Group ID is not null\n") 
        print("WARNING, Employee Group ID is not null\n")   
        
    if len(tokens[9]) != 0:
        file.write("WARNING, Employee Class is not null\n") 
        print("WARNING, Employee Class is not null\n")
    
    
def checkVAC(tokens):
    global file
    global errors
    
    if len(tokens[0]) != 0:
        file.write("WARNING, Section code is not null for VAC\n") 
        print("WARNING, Section code is not null for VAC\n")

    if len(tokens[1]) != 0 and checkDate(tokens[1]) == False:
        file.write("WARNING, invalid VAC Coverage Effective Date\n" + tokens[1] + '\n') 
        print("WARNING, invalid VAC Coverage Effective Date\n" + tokens[1] + '\n') 
        
    if len(tokens[2]) != 0 and checkDate(tokens[2]) == False:
        file.write("WARNING, VAC Coverage Termination Description is not null\n") 
        print("WARNING, VAC Coverage Termination Description is not null\n")    
        
    if len(tokens[3]) != 0:
        file.write("WARNING, VAC Coverage Termination Reason Code is not null\n") 
        print("WARNING, VAC Coverage Termination Reason Code is not null\n") 
        
    if len(tokens[4]) != 0:
        file.write("WARNING, VAC Coverage Termination Description is not null\n") 
        print("WARNING, VAC Coverage Termination Description is not null\n")
        
    if len(tokens[5]) != 0 and tokens[5] not in ['1', '2', '3', '4', '5']:
        file.write("WARNING, invalid VAC Benefit Amount\n" + tokens[5] + '\n') 
        print("WARNING, invalid VAC Benefit Amount\n" + tokens[5] + '\n')
        
    if len(tokens[6]) != 0 and tokens[6] not in ['Option 1', 'Option 2']:
        file.write("WARNING, invalid VAC Plan Option\n" + tokens[5] + '\n') 
        print("WARNING, invalid VAC Plan Option\n" + tokens[5] + '\n')
    
    if len(tokens[7]) != 0 and tokens[7] != '001': #changed from 1225486 to 001 for CI & ACC
        file.write("WARNING, invalid VAC Plan Number\n" + tokens[5] + '\n') 
        print("WARNING, invalid VAC Plan Number\n" + tokens[5] + '\n')
    
    if len(tokens[8]) != 0:
        file.write("WARNING, VAC Employee Group ID is not null\n") 
        print("WARNING, VAC Employee Group ID is not null\n")   
        
    if len(tokens[9]) != 0:
        file.write("WARNING, VAC Employee Class is not null\n") 
        print("WARNING, VAC Employee Class is not null\n")        
        
        
'''
Check that the row count matches the ftr record scount
'''
def checkFTR(tokens):
    global cntr
    global errors
    global file
    
    if len(tokens) < 2:
        file.write('ERROR: No footer count\n')        
        print("ERROR: No footer count\n")
        return
        
    numA = str(cntr - 2)
    numB = tokens[1]    
    if str(cntr-2) != tokens[1].strip():
        file.write("WARNING, footer count does not match records count\n")
        file.write("FOOTER: " + tokens[1] + '\n')
        file.write("ROW COUNT: " + str(cntr -2) + '\n')        
        print("WARNING, footer count does not match records count\n")
        print("FOOTER: " + tokens[1] + '\n')
        print("ROW COUNT: " + str(cntr -2) + '\n')
        errors += 1

'''
Start Main script here
'''
path = 'H:\\'  # get current path
print(path)
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

file = open(path + '\\logs\\HartfordEDILog' + time + '.txt', 'w+')  
file.write("starting Hartford EDI check at " + time + '\n')  # write to log
file.write("using EDI: " + edi_path + '\n')
print("using EDI: " + edi_path + '\n')

with open(edi_path, 'r') as edif:
    content = edif.readlines()
    
SIZE = len(content)

file.write("There are " + str(SIZE) + " lines in the EDI\n")    

cntr = 1
errors = 0
tempName = os.path.basename(edi_path)
#outFileName = edi_path.replace(tempName,"") + "TEST_" + tempName
#ediOut = open(outFileName, 'w')
scodes = ['PII', 'ECI', 'EMI', 'NST', 'LTD', 'VCI', 'VAC', 'HDR', 'FTR']
rcodes = ['SP', 'CH', 'SI', 'PA', 'TR', 'GC', 'GP', 'OT', 'UN', '']
mcodes = ['M', 'I', 'D', 'S', 'C', 'W', 'N', 'P', 'X', 'U']
statcodes = ['A', 'I', 'L', 'T', 'R', 'D', 'P']
dependent = True

for line in content: #step through every line
    
    ''' this section removes empty EDI sections, no longer needed.
    if('~NST~||||||||' in line):
        line = line.strip().replace('~NST~||||||||',"")
    
    if('~LTD~||||||||||' in line):
        line = line.strip().replace('~LTD~||||||||||',"")
    
    if('~VCI~||||||||||' in line):
        line = line.strip().replace('~VCI~||||||||||',"")
    
    if('~VAC~|||||||||' in line):
        line = line.strip().replace('~VAC~|||||||||',"")
    '''
    
    p = re.compile(r'~(.*?)~')
    parts = p.split(line)
    del parts[0] #remove empty element
    numParts = len(parts)
    partCntr = 0;
    
    while(partCntr <= numParts - 2):
        if(parts[partCntr] not in scodes):
            errors +=1
            print('Warning! Invalid section code: ' + parts[0] + '\n')
            print('Can\'t check this section without knowing what section it\'s suppossed to be\n')
        else:
            tokens = parts[partCntr+1].split("|")
            
            #clean up tokens (mostly endlines)
            for x in range(len(tokens)):
                tokens[x] = tokens[x].strip() 
            
            if parts[partCntr] == 'PII':
               checkPII(tokens)
            elif parts[partCntr] == 'HDR':
               checkHDR(tokens)
            elif parts[partCntr] == 'ECI':
               checkECI(tokens)
            elif parts[partCntr] == 'EMI' and dependent == False:
               checkEMI(tokens)
            elif parts[partCntr] == 'NST':
                checkNST(tokens)
            elif parts[partCntr] == 'LTD':
                checkLTD(tokens)
            elif parts[partCntr] == 'VCI':
                checkVCI(tokens)
            elif parts[partCntr] == 'VAC':
                checkVAC(tokens)
            elif parts[partCntr] == 'FTR':
                checkFTR(tokens)
                break;
        partCntr += 2
        
    #print(parts)
    dependent = True
    
    #check if the line ends with break. if not add one
    #why would it not end with a line break? stip()?
#     if line.endswith('\n'):
#         ediOut.write(line)
#     else:
#         ediOut.write(line + '\n')
    cntr += 1
    file.write('Done with line ' + str(cntr) + '\n')
    #print('Done with line ' + str(cntr) + '\n')
    
    
#ediOut.close()
SIZE = len(content) # get the number of rows
print("Scan completed, there are " + str(errors) + " errors in the file")
file.write("Scan completed, there are " + str(errors) + " errors in the file")
print("checked a total of " + str(SIZE-2) + " records")
file.write("checked a total of " + str(SIZE-2) + " records")
file.close()

#wait for ack if any errors were found.
if errors > 0:
    input("Press Enter to continue")
    