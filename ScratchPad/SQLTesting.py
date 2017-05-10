'''
Created on Mar 10, 2017

@author: jchavis
'''
import pyodbc, sys
# print(pyodbc.drivers())
conn = pyodbc.connect(
    r'DRIVER={SQL Server};'
    r'SERVER=RALIMSQL1\RALIM1;'
    r'DATABASE=CAMSRALFG;'
    r'UID=PerfMon;'
    r'PWD=N@g1oscheck'
    )


cursor = conn.cursor()
str = "SELECT Client.[First Name] FROM Client WHERE Client.[Client#] = -3"
#print(str)
cursor.execute(str)
for row in cursor.fetchall():
    print(row[0])