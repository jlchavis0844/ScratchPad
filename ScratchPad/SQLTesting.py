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
str = "SELECT Client.* FROM Client WHERE Client.[Last Name] = 'Chavis'"
#print(str)
cursor.execute(str)
for row in cursor.fetchall():
    print(row)