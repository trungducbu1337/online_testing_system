import pandas as pd
from datetime import datetime


class AttendanceMarker:
    def __init__(self, path_to_csv):
        self.path_csv = path_to_csv
        self.__create_csv()

    def __create_csv(self):
        with open(self.path_csv, 'w', encoding='UTF8', newline='') as f:
            f.writelines('Name,Arrival time')

    def remove_blanklines_csv(self):
        df = pd.read_csv(self.path_csv)
        # Dropping the empty rows
        modified_df = df.dropna()
        # Saving it to the csv file
        modified_df.to_csv(self.path_csv, index=False)

    def remove_specific_row_from_csv(self, column_name, *args):
        """
        Param list:
        :param column_name: The column that determines which row will be
               deleted
        :param args: Strings from the rows according to the conditions with
                     the column
        """
        row_to_remove = []
        for row_name in args:
            row_to_remove.append(row_name)
        try:
            df = pd.read_csv(self.path_csv)
            for row in row_to_remove:
                df = df[eval("df.{}".format(column_name)) != row]
            df.to_csv(self.path_csv, index=False)
        except Exception:
            raise Exception("Error message....")

    def get_student_data(self):
        self.remove_blanklines_csv()
        with open(self.path_csv, 'r', encoding='UTF8', newline='') as f:
            data_list = f.readlines()
        return data_list[1:]

    def mark_attendance(self, name):
        with open(self.path_csv, 'r+', encoding='UTF8', newline='') as f:
            data_list = f.readlines()
            name_list = []
            for line in data_list:
                entries = line.split(',')
                name_list.append(entries[0])
            if name not in name_list:
                now = datetime.now()
                date_time = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{date_time}')
