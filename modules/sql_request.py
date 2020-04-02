import sqlite3

def outp_correct(data_all):
    x_c = 0
    y_c = 0
    while y_c <= len(data_all)-1:
        while x_c <= len(data_all[y_c])-1:
            if data_all[y_c][x_c] and type(data_all[y_c][x_c]).__name__ == 'str' and ':$"$:' in str(data_all[y_c][x_c]):
                data_all[y_c] = list(data_all[y_c])
                print(data_all[y_c])
                data_all[y_c][x_c] = data_all[y_c][x_c].replace(':$"$:', "'")
            x_c += 1
        x_c = 0
        y_c += 1
    return data_all

class DataBase:
    version = '0.1 Test'
    def __init__(self, data_base_file):
        self.conn = sqlite3.connect(data_base_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def add_table(self, name, columns, PRIMARY_KEYS=None):
        types = {   'TEXT': 'TEXT', 
                    'text': 'TEXT', 
                    'str': 'TEXT',  
                    'INTEGER': 'INTEGER', 
                    'integer': 'INTEGER', 
                    'int': 'INTEGER'}
        if "'" in str(name):
            print("\nATTENTION: FOR NORMAL OPERATIONAL ABILITY OF DB, WE CHANGED THE SIGN ' to \" ( " + str(name) + " => " + str(name).replace("'", '"') + " ).\n")
        request_data = "CREATE TABLE '" + str(name).replace("'", '"') + "' ("
        if type(columns).__name__ == 'dict':
            for column in columns:
                type_n = columns.get(column)
                if type_n and type_n != '' and type_n in types:
                    request_data += '"' + column + '" ' + types.get(type_n) + ','
        elif type(columns).__name__ == 'str':
            request_data += '"' + columns + '" TEXT,'
        if PRIMARY_KEYS and type(PRIMARY_KEYS).__name__ == 'str':
            request_data += 'PRIMARY KEY("id"));'
        else:
            request_data = request_data[:len(request_data)-1] + ');'
        self.cursor.execute(request_data)
        self.conn.commit()
        return True


    def request(self, request, args=None):
        if args:
            request_data = self.cursor.execute(request, args).fetchall()
        else:
            request_data = self.cursor.execute(request).fetchall()
        self.conn.commit()
        return outp_correct(request_data)