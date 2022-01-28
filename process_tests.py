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

def get_average_troops(df):
    count_1 = 0
    count_2 = 0
    total_1 = 0
    total_2 = 0

    for index, row in df.iterrows():
        troops = row[1].split()
        winner = row[0].split()

        troops = int(troops[-1])
        winner = int(winner[-1])

        if winner == 1:
            total_1 += int(troops)
            count_1 += 1
        else:
            total_2 += int(troops)
            count_2 += 1

    average_troops_1 = total_1 / count_1
    average_troops_2 = total_2 / count_2
        
    return average_troops_1, average_troops_2

paths = []
for file in os.listdir('tests'):
    if file.endswith(".txt"):
        if 'montecarlo' in file:
            paths.append('tests/' + file)

for path in paths:
    df = get_data(path)
    file_exchange = get_average_file_exchange(df)
    victory_percentage = get_victory_percentage(df)
    execution_time = get_average_execution_time(df)
    troops_p1, troops_p2 = get_average_troops(df)

    print(path, '\n')
    print('Victory Percentage:', victory_percentage)
    print('File Exchange:', file_exchange)
    print('p1 troops:', troops_p1)
    print('p2 troops:', troops_p2)
    print('Execution Time:', execution_time)
    print('---------------------------------------')