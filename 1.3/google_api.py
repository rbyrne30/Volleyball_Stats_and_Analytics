import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from stats_config import POSITIONS, SERVETYPES

with open("settings.json", "r") as f:
    _settings = json.load(f)

class Sheets(object):
    """Takes in a dictionary in style referenced by 'format_by_volley' and
    outputs to google sheets"""
    def __init__(self, D, worksheet_num):
        ################# THIS STAYS CONSTANT #########################
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(_settings['JSON_KEY_FILE'], scope)
        gc = gspread.authorize(credentials)
        doc_url = _setting["DOC_URL"]
        sheet = gc.open_by_url(doc_url)
        worksheet = sheet.get_worksheet(worksheet_num)
        ###############################################################
        self.clearWorksheet(worksheet)
        buffer = 4
        hitting_table_height = self.outputHitting(worksheet, 1, D['hitting'])
        serving_table_height = self.outputServing(worksheet, hitting_table_height + buffer + 1, D['serving'])
        setting_table_height = self.outputSetting(worksheet, hitting_table_height + serving_table_height + 2 * buffer + 1, D['setting'])
        passing_table_height = self.outputPassing(worksheet, hitting_table_height + serving_table_height + setting_table_height + 3 * buffer + 1, D['passing'])

    def clearWorksheet(self, worksheet):
        cells = worksheet.range("A1:Z500")
        for cell in cells:
            cell.value = ""
        worksheet.update_cells(cells)


    def getPassingTableHeight(self, D):
        """Assumes D['passing'] as D"""
        height = 2
        for player in D['players']:
            height += 2
            for type in D['players'][player]['servetype']:
                height += 1
        return height



    def outputPassing(self, worksheet, y, D):
        """Assumes D['passing'] as D"""
        height = self.getPassingTableHeight(D)
        cells = worksheet.range("A%d:H%d" %(y, y + height))
        table = []
        while cells != []:
            table += [cells[:8]]
            cells = cells [8:]

        y = 0
        x = 0

        header = ['PASSING', 'PCT', 'ATP']
        header_info = ['', "%.3f" %(D['track'] / D['attempts']) if D['attempts'] > 0 else 0, D['attempts']]
        for i in range(len(header)):
            table[y][x+i].value = header[i]
            table[y+1][x+i].value = header_info[i]

        x += 1
        y += 2
        base_x = x

        header = ['Player', 'PCT', 'ATP', '', 'Type', 'PCT', 'ATP']

        for player in D['players']:
            y += 1
            player_dict = D['players'][player]
            for i in range(len(header)):
                table[y][x+i].value = header[i]

            y += 1

            b1 = [player, '%.3f' %(player_dict['track']/player_dict['attempts']), player_dict['attempts']]
            for i in range(len(b1)):
                table[y][x+i].value = b1[i]

            x += len(b1) + 1

            for type in player_dict['servetype']:
                type_dict = player_dict['servetype'][type]
                info = [SERVETYPES[type], "%.3f" %(type_dict['track']/type_dict['attempts']), type_dict['attempts']]
                for i in range(len(info)):
                    table[y][x+i].value = info[i]
                y += 1
            x = base_x
        cells = []
        for row in table:
            for cell in row:
                cells.append(cell)
        worksheet.update_cells(cells)
        return height


    def getSettingTableHeight(self, D):
        """Assumes D['setting'] as D"""
        height = 1

        for row in D['rows']:
            height += 2
            for pos in D['rows'][row]['position']:
                height += 1
        return height


    def outputSetting(self, worksheet, y, D):
        """Assumes taking D['setting'] as D"""
        height = self.getSettingTableHeight(D)
        cells = worksheet.range("A%d:F%d" %(y, y + height))
        table = []
        while cells != []:
            table += [cells[:6]]
            cells = cells[6:]

        y = 0
        x = 0

        table[y][x].value = 'SETTING'

        x += 1
        base_x = x

        header = ['Row', 'Pos', 'PCT', 'ATP', 'SO PCT']

        for row in D['rows']:
            for i in range(len(header)):
                table[y][x+i].value = header[i]

            y += 1

            table[y][x].value = row

            x += 1

            for pos in D['rows'][row]['position']:
                pos_dict = D['rows'][row]['position'][pos]
                pct = pos_dict['total'] / D['rows'][row]['total']
                info = [POSITIONS[pos], "%.3f" %pct, pos_dict['total'], pos_dict['track'] / pos_dict['total']]
                for i in range(len(info)):
                    table[y][x+i].value = info[i]
                y += 1
            x -= 1
            y += 1

        cells = []
        for row in table:
            for cell in row:
                cells.append(cell)
        worksheet.update_cells(cells)
        return height


    def getServingTableHeight(self, D):
        """Assumes D['serving'] as D"""
        height = 2

        for player in D['players']:
            height += 2
            for type in D['players'][player]['servetype']:
                for spot in D['players'][player]['servetype'][type]['spots']:
                    height += 1
        return height


    def outputServing(self, worksheet, y, D):
        """Assumes D['serving'] as D"""
        height = self.getServingTableHeight(D)
        cells = worksheet.range("A%d:K%d" %(y, y + height))
        table = []
        while cells != []:
            table += [cells[:11]]
            cells = cells[11:]

        y = 0
        x = 0

        header = ['SERVING', 'ATP', 'Aces', 'Errors']
        header_info = [' ', D['attempts'], D['aces'], D['errors']]
        for i in range(len(header)):
            table[y][x+i].value = header[i]
            table[y+1][x+i].value = header_info[i]

        x += 1
        y += 2
        base_x = x
        base_y = y

        header = ['Player', 'ATP', 'Aces', 'Errors', 'Type', 'Spot', 'PCT', 'ATP', 'Aces', 'Errors']
        for player in D['players']:
            player_dict = D['players'][player]
            y+= 1

            for i in range(len(header)):
                table[y][x+i].value = header[i]
            y += 1

            b1_info = [player, player_dict['attempts'], player_dict['aces'], player_dict['errors']]
            for i in range(len(b1_info)):
                table[y][x+i].value = b1_info[i]

            x += len(b1_info)

            for servetype in player_dict['servetype']:
                type_dict = player_dict['servetype'][servetype]
                table[y][x].value = SERVETYPES[servetype]
                x += 1

                for spot in type_dict['spots']:
                    spot_dict = type_dict['spots'][spot]
                    pct = spot_dict['attempts'] / type_dict['attempts']
                    b3_block = [spot, "%.3f" %pct, spot_dict['attempts'], spot_dict['aces'], spot_dict['errors']]
                    for i in range(len(b3_block)):
                        table[y][x+i].value = b3_block[i]
                    y += 1
                x -= 1
            x = base_x

        #convert table to list
        cells = []
        for row in table:
            for cell in row:
                cells.append(cell)
        worksheet.update_cells(cells)
        return height


    def getHittingTableHeight(self, D):
        """Assumes taking in D['hitting'] as D"""
        height = 2

        for player in D['players']:
            height += 2
            for pos in D['players'][player]['position']:
                for shot in D['players'][player]['position'][pos]['shot']:
                    height += 1
        return height


    def outputHitting(self, worksheet, y, D):
        #format cells into tables
        #for accessing with x, y coordinates
        height = self.getHittingTableHeight(D)
        cells = worksheet.range("A%d:R%d" %(y, y + height))

        table = []
        while cells != []:
            table += [cells[:18]]
            cells = cells[18:]

        #output data
        x = 0
        y = 0

        team_attempts = D['attempts']
        team_kills = D['kills']
        team_errors = D['errors']

        #header
        header = ['HITTING', 'PCT', 'ATP', 'K', 'E']
        header_info = [" ", "%.3f" %((team_kills-team_errors)/team_attempts) if team_attempts > 0 else 0, team_attempts, team_kills, team_errors]
        for i in range(len(header)):
            table[y][x+i].value = header[i]
            table[y+1][x+i].value = header_info[i]

        #player stats
        x += 1
        y += 2
        base_x = x
        base_y = y

        header = ['PLAYER', 'PCT', 'ATP', 'K', 'E', " ",
                    'POS', 'PCT', 'ATP', 'K', 'E', " ",
                    'SHOT', 'PCT', 'ATP', 'K', 'E']

        for player in D['players']:
            x = base_x
            y += 1
            for i in range(len(header)):
                table[y][x+i].value = header[i]

            y += 1
            #block1
            player_dict = D['players'][player]
            player_attempts = player_dict['attempts']
            player_kills = player_dict['kills']
            player_errors = player_dict['errors']
            b1_info = [player, "%.3f" %((player_kills-player_errors)/player_attempts), player_attempts, player_kills, player_errors]

            for i in range(len(b1_info)):
                table[y][x+i].value = b1_info[i]

            x += len(b1_info) + 1

            #block2
            pos_dict = player_dict['position']
            for pos in pos_dict:
                pos_attempts = pos_dict[pos]['attempts']
                pos_kills = pos_dict[pos]['kills']
                pos_errors = pos_dict[pos]['errors']
                pos_info = [POSITIONS[pos], "%.3f" %((pos_kills-pos_errors)/pos_attempts), pos_attempts, pos_kills, pos_errors]
                for i in range(len(pos_info)):
                    table[y][x+i].value = pos_info[i]

                #block3
                x += len(pos_info) + 1
                shot_dict = pos_dict[pos]['shot']
                for shot in shot_dict:
                    shot_attempts = shot_dict[shot]['attempts']
                    shot_kills = shot_dict[shot]['kills']
                    shot_errors = shot_dict[shot]['errors']
                    shot_info = [shot, "%.3f" %((shot_kills-shot_errors)/shot_attempts), shot_attempts, shot_kills, shot_errors]
                    for i in range(len(shot_info)):
                        table[y][x+i].value = shot_info[i]
                    y += 1
                x = base_x + len(b1_info) + 1

        #convert table back to single list
        L = []
        for row in table:
            for cell in row:
                L.append(cell)
        #update cells
        worksheet.update_cells(L)
        return height
