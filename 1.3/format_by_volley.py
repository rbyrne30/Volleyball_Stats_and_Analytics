from stats_config import POSITIONS, SPOTS, SHOTS, SERVETYPES, PASSRATINGS, HITTING_KER, SERVING_KER
import os

class Format(object):
    """
    Formats a text file written as:
    #R - [type][player#][rating]...[choice][shot][KER][hitter#]...
    #S - [player#][type][spot][KER]...[choice][shot][KER][hitter#]...
    into a dictionary as:
    D = {
      'hitting': {
        'attempts': (int)
        'kills': (int),
        'errors': (int).
        'players': {
          (string): {
            'attempts': (int),
            'kills': (int),
            'errors': (int),
            'position': {
              (string): {
                'attempts': (int),
                'kills': (int),
                'errors': (int),
                'shot': {
                  (string): {
                    'attempts': (int),
                    'kills': (int),
                    'errors': (int)
                  }
                }
              }
            }
          }
        }
      },
      'setting': {
        'total': (int),
        'rows': {
          (int): {
            'total': (int)
            'position': {
              (string): {
                'total': (int),
                'track': (int)
              },
              'rating': {
                'total': (int),
                (string): {
                  'position': {
                    (string): {
                      'total': (int),
                      'track': (int)
                    }
                  }
                }
              }
            }
          }
        }
      },
      'passing': {
        'attempts': (int),
        'track': (int)
        'players': {
          (string): {
            'attempts': (int),
            'track': (int),
            'servetype': {
              (string): {
                'attempts': (int),
                'track': (int)
              }
            }
          }
        }
      },
      'serving': {
        'attempts': (int),
        'aces': (int),
        'errors': (int)
        'spots': {
          (string): {
            'attempts': (int),
            'aces': (int),
            'errors': (int)
          }
        },
        'players': {
          (string): {
              'attempts': (int),
              'aces': (int),
              'errors': (int),
              'spots': {
                (string): {
                  'attempts': (int),
                  'aces': (int),
                  'errors': (int)
                }
              },
              'servetype': {
                (string): {
                  'attempts': (int),
                  'aces': (int),
                  'errors': (int),
                  'spots': {
                    (string): {
                      'attempts': (int),
                      'aces': (int),
                      'errors': (int)
                    }
                  }
                }
              }
            }
        }
      }
    }
    """
    def __init__(self, lines):
        self.dictionary = self.create_dict(lines)


    def create_dict(self, lines):
        D = {'hitting': {'attempts': 0, 'kills': 0, 'errors': 0, 'players': {}},
            'setting': {'total': 0, 'rows':{}},
            'serving': {'attempts': 0, 'track': 0, 'aces': 0, 'errors': 0, 'spots': {}, 'players': {}},
            'passing': {'attempts': 0, 'track': 0, 'players': {}}}

        if lines == []:
            raise ValueError("Lines to be analyzed were empty!")

        cur_row = int(self.getStartingRow(lines)) % 6
        if cur_row == 0:
            cur_row = 6
        # lines = lines[1:]

        new_server = False

        for i in range(len(lines)):
            line = lines[i]
            line = line.strip()
            if line == "":
                continue

            if line[0] == '*':
                cur_row = int(self.getStartingRow([lines[i]])) % 6
                if cur_row == 0:
                    cur_row = 6
                new_server = False
                continue


            if self.isServing(line):
                if new_server:
                    cur_row = (cur_row + 1) % 6
                    if cur_row == 0:
                        cur_row = 6
                    new_server = False
                self.getServingInfo(line, D['serving'])
                self.getHittingInfo(line[5:], D['hitting'])
            elif self.isReceiving(line):
                new_server = True
                if line[1] == '-':
                    continue
                self.getPassingInfo(line, D['passing'])
                self.getSettingInfo(line, cur_row, D['setting'])
                self.getHittingInfo(line[4:], D['hitting'])


        return D


    def getStartingRow(self, lines):
        for line in lines:
            for c in line:
                if c.isdigit():
                    return int(c)
        return None


    def isReceiving(self, line):
        """Assumes line is valid and not commented"""
        return line[0] in SERVETYPES


    def isServing(self, line):
        """Assumes line is valid and not commented"""
        return line[0].isdigit() and line[1].isdigit()


    def addSettingInfoToDic(self, choice, outcome, D):
        D['total'] += 1
        D['track'] += HITTING_KER[outcome]


    def getSettingInfo(self, line, row, D):
        """Assumes taking D['setting'] as D"""
        choice = line[4:6]
        rating = int(line[3])

        if choice == "no":
            return D
        elif choice == "dp":
            outcome = line[6]
        else:
            outcome = line[7]

        D['total'] += 1

        if not row in D['rows']:
            D['rows'][row] = {'total': 0, 'position': {}, 'rating': {}}
        D['rows'][row]['total'] += 1

        if not choice in D['rows'][row]['position']:
            D['rows'][row]['position'][choice] = {'total': 0, 'track': 0}
        self.addSettingInfoToDic(choice, outcome, D['rows'][row]['position'][choice])

        if not rating in D['rows'][row]['rating']:
            D['rows'][row]['rating'][rating] = {'total': 0, 'position': {}}
        D['rows'][row]['rating'][rating]['total'] += 1

        if not choice in D['rows'][row]['rating'][rating]['position']:
            D['rows'][row]['rating'][rating]['position'][choice] = {'total': 0, 'track': 0}
        self.addSettingInfoToDic(choice, outcome, D['rows'][row]['rating'][rating]['position'][choice])


    def addPassingInfoToDic(self, rating, D):
        D['attempts'] += 1
        D['track'] += int(rating)


    def getPassingInfo(self, line, D):
        """Assumes taking D['passing'] as D"""
        servetype = line[0]
        player = line[1:3]
        rating = line[3]

        self.addPassingInfoToDic(rating, D)

        if not player in D['players']:
            D['players'][player] = {'servetype': {}, 'attempts': 0, 'track': 0}
        self.addPassingInfoToDic(rating, D['players'][player])

        if not servetype in D['players'][player]['servetype']:
            D['players'][player]['servetype'][servetype] = {'attempts': 0, 'track': 0}
        self.addPassingInfoToDic(rating, D['players'][player]['servetype'][servetype])


    def addHittingInfoToDic(self, outcome, D):
        D['attempts'] += 1
        D['kills'] += 1 if outcome == 'k' else 0
        D['errors'] += 1 if outcome == 'e' else 0


    def getHittingInfo(self, line, D):
        """Assumes taking in D['hitting'] as D"""
        if line == "" or line[:2] == "no":
            return D

        position = line[:2]

        if position == "dp":
            outcome = line[2]
            player = line[3:5]
            shot = "dp"
            line = line[5:]
        else:
            shot = line[2]
            outcome = line[3]
            player = line[4:6]
            line = line[6:]

        self.addHittingInfoToDic(outcome, D)

        if not player in D['players']:
            D['players'][player] = {'attempts': 0, 'kills': 0, 'errors': 0, 'position': {}}
        self.addHittingInfoToDic(outcome, D['players'][player])

        if not position in D['players'][player]['position']:
            D['players'][player]['position'][position] = {'attempts': 0, 'kills': 0, 'errors': 0, 'shot': {}}
        self.addHittingInfoToDic(outcome, D['players'][player]['position'][position])

        if not shot in D['players'][player]['position'][position]['shot']:
            D['players'][player]['position'][position]['shot'][shot] = {'attempts': 0, 'kills': 0, 'errors': 0}
        self.addHittingInfoToDic(outcome, D['players'][player]['position'][position]['shot'][shot])

        return self.getHittingInfo(line, D)


    def addServingInfoToDic(self, servetype, outcome, D):
        D['attempts'] += 1
        D['aces'] += 1 if outcome == 'k' else 0
        D['errors'] += 1 if outcome == 'e' else 0


    def getServingInfo(self, line, D):
        """Assumes taking in D['serving'] as D"""
        player = line[:2]
        servetype = line[2]
        spot = line[3]
        outcome = line[4]

        self.addServingInfoToDic(servetype, outcome, D)

        if not spot in D['spots']:
            D['spots'][spot] = {'attempts': 0, 'track': 0, 'aces': 0, 'errors': 0}
        self.addServingInfoToDic(servetype, outcome, D['spots'][spot])

        if not player in D['players']:
            D['players'][player] = {'attempts': 0, 'track': 0, 'aces': 0, 'errors': 0, 'spots': {}, 'servetype': {}}
        self.addServingInfoToDic(servetype, outcome, D['players'][player])

        if not spot in D['players'][player]['spots']:
            D['players'][player]['spots'][spot] = {'attempts': 0, 'track': 0, 'aces': 0, 'errors': 0}
        self.addServingInfoToDic(servetype, outcome, D['players'][player]['spots'][spot])

        if not servetype in D['players'][player]['servetype']:
            D['players'][player]['servetype'][servetype] = {'attempts': 0, 'track': 0, 'aces': 0, 'errors': 0, 'spots': {}}
        self.addServingInfoToDic(servetype, outcome, D['players'][player]['servetype'][servetype])

        if not spot in D['players'][player]['servetype'][servetype]['spots']:
            D['players'][player]['servetype'][servetype]['spots'][spot] = {'attempts': 0, 'track': 0, 'aces': 0, 'errors': 0}
        self.addServingInfoToDic(servetype, outcome, D['players'][player]['servetype'][servetype]['spots'][spot])






class FileChecker(object):
    """Checks if file is properly formatted as:
    #R - [type][player#][rating]...[choice][shot][KER][hitter#]...
    #S - [player#][type][spot][KER]...[choice][shot][KER][hitter#]...

    Ignores lines with a comment (begins with '#')
    Marks lines that are not formatted properly.
    """

    def __init__(self, files, output_file):
        # default_file_name = "Checked_Files_("+len(files)+")"
        self.files = files
        self.output_file = output_file
        self.lines = self.check_files()


    def check_files(self):
        files = self.files
        output_file = self.output_file
        all_lines = []
        for file in files:
            if not os.path.isfile(file):
                print("File does not exist: %s" %file)
                continue

            with open(file, "r") as myfile:
                #mark invalid lines
                validated = self.validate(myfile.readlines())
                #append to total lines
                lines = validated[1]
                invalid_count = validated[0]
                all_lines += lines
                #if there are invalid lines then print number
                if invalid_count > 0:
                    print("%d invalid lines in file: %s" %(invalid_count, file))

            with open(file, 'w') as myfile:
                for line in lines:
                    myfile.write(line)


        #write lines to output_file
        with open(output_file, 'w') as myfile:
            for line in all_lines:
                myfile.write(line)
        return all_lines


    def isReceiving(self, line):
        if len(line) > 3:
            serveType = line[0]
            player = line[1:3]
            passRating = line[3]

            if serveType in SERVETYPES and player.isdigit() and passRating in PASSRATINGS:
                return [serveType, player, passRating]
        elif line[0] in SERVETYPES and line[1] == '-':
            return True

        return False


    def isServing(self, line):
        if len(line) > 4:
            player = line[:2]
            serveType = line[2]
            spot = line[3]
            serveOutcome = line[4]

            if player.isdigit() and serveType in SERVETYPES and spot in SPOTS and serveOutcome in SERVING_KER:
                return [player, serveType, spot, serveOutcome]

        return False


    def isValidHelper(self, segment):
        if segment[:2] == 'dp':
            if len(segment) < 5:
                return False
            hit_ker = segment[2]
            if hit_ker in HITTING_KER and segment[3].isdigit() and segment[4].isdigit():
                segment = segment[5:]
            else:
                return False

        if segment[:2] == 'no':
            return len(segment) < 3

        if segment == "":
            return True

        if len(segment) % 6 == 0 and len(segment) >= 6:
            choice = segment[:2]
            shot = segment[2]
            hit_ker = segment[3]
            hitter = segment[4:6]

            if choice in POSITIONS and shot in SHOTS and hit_ker in HITTING_KER and hitter.isdigit():
                return self.isValidHelper(segment[6:])

        return False


    def isValid(self, line):
        if self.isReceiving(line):
            return self.isValidHelper(line[4:])

        elif self.isServing(line):
            return self.isValidHelper(line[5:])

        return False


    def validate(self, lines):
        """Checks file for proper formatting. Marks line if incorrect and returns all lines with markings."""
        checked_lines = []
        invalid = 0
        for line in lines:
            line = line.strip()

            if line == "":
                checked_lines.append("\n")
            elif line[0] == "#" or line[0] == '*' or self.isValid(line):
                checked_lines.append(line + "\n")
            else:
                checked_lines.append("###[ Invalid line ]### " + line + "\n")
                invalid += 1
        return [invalid, checked_lines]
