bcolors = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

def log(message, color='', format=''):
    if format and 'b' in format:
        message = bcolors['BOLD'] + message
    if format and 'u' in format:
        message = bcolors['UNDERLINE'] + message
    if color in bcolors:
        message = bcolors[color] + message
    message += bcolors['ENDC']
    print(message)
