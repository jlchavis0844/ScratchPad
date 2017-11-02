import os, sys, csv
from pathlib import Path
owners = {}

my_file = Path(".\\logs\\MERGES_test.csv")
print("Does test file exist? " + str(my_file.is_file()))
print(os.path.abspath(my_file))