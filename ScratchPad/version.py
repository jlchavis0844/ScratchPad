import sys
print(sys.version)

Result: iif(((SELECT COUNT(*) FROM Client) > 10), "Working", "BROKEN")