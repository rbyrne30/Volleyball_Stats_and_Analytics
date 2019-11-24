from format_by_volley import Format, FileChecker
from google_api import Sheets
import sys
import os
import json

class Main(object):
    def __init__(self, files, worksheet_num):
        lines = FileChecker(files, '/tmp/checkFiles.txt').lines
        D = Format(lines).dictionary
        Sheets(D, worksheet_num)



if __name__ == "__main__":
    args = sys.argv

    if len(args) == 2 and args[1] == 'help':
        print("""
    This program analyzes the statistics of a volleyball
    match based on the users inputted files. The statistical
    analysis of these files will be outputted to google sheets
    specified by the API key and under the tab specified by the
    user. This google doc can be shared to other users and
    updated on the fly.

    Usage: python3 main.py <tab#> <file> [,file2, ...]

    <tab#> - tab # for google sheets
            - 0 -> first tab
            - 1 -> second tab
            - etc.

    <file> - file you wish to analyze
            - include full path to file

    [,file2, ...] - other files you wish to analyze
                alongside the first input file
        """)
        exit()

    if len(args) < 3:
        print("For help type: python3 main.py help\n")
        print("Usage: python3 main.py <tab#> <file> [,file2, ...]")
        exit()

    tab = args[1]
    files = args[2:]

    if not tab.isnumeric():
        print("User input 'tab' is not a number: %s" %str(tab))
        exit()
    tab = int(tab, 10)

    for file in files:
        if not os.path.isfile(file):
            print("File not found: %s" %str(file))
            exit()

    Main(files, tab)
