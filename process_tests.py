import pandas
import os

def get_data(path):
    df = pandas.read_csv(path, header=None)

    return df

def get_average_file_exchange(df):
    size = len(df[2])
    total = 0

    for row in df[2]:
        row = row.split()
        total += int(row[-1])

    return total / size

def get_victory_percentage(df):
    size = len(df[0])

    count = 0
    for row in df[0]:
        row = row.split()
        player = int(row[-1])

        if player == 1:
            count += 1

    return count / size

def get_average_execution_time(df):
    size = len(df[5])
    total = 0

    for row in df[5]:
        row = row.split()
        total += float(row[-1])

    return total / size

paths = []
for x in os.listdir('tests'):
    if x.endswith(".txt"):
        paths.append('tests/' + x)

for path in paths:
    df = get_data(path)
    file_exchange = get_average_file_exchange(df)
    victory_percentage = get_victory_percentage(df)
    execution_time = get_average_execution_time(df)

    print('----', path, '----', sep='')

    print('File Exchange:', file_exchange)
    print('Victory Percentage:', victory_percentage)
    print('Execution Time:', execution_time)