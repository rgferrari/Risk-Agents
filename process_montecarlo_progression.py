import pandas
import os

def get_data(path):
    df = pandas.read_csv(path, header=None)

    return df

def get_victory_percentage_along_iterations(df) -> list:
    current_size = 0
    count = 0

    victory_percentage_along_iterations = []

    for row in df[0]:
        row = row.split()
        player = int(row[-1])

        if player == 1:
            count += 1
        
        current_size += 1

        if current_size % 100 == 0:
            victory_percentage = count / current_size
            victory_percentage_along_iterations.append((current_size, victory_percentage * 100))

    return victory_percentage_along_iterations

paths = []
for file in os.listdir('tests'):
    if file.endswith(".txt"):
        if 'montecarlo_fixed' in file:
            paths.append('tests/' + file)

for path in paths:
    df = get_data(path)

    print(path, '\n')

    victory_percentage_along_iterations = get_victory_percentage_along_iterations(df)

    for v in victory_percentage_along_iterations:
        print(v)