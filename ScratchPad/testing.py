import os, sys, csv
from pathlib import Path
owners = {}

my_file = Path(".\owners.csv")
print(my_file.is_file())
print(os.path.abspath(my_file))