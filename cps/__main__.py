import os
from time import perf_counter


READ_FLAGS = (TAGS, MOVES, END) = (0, 1, 2)


dir = "data"

flag = END

games = []


t = perf_counter()


for filename in os.listdir(dir):
    path = os.path.join(dir, filename)
    with open(path, "r") as f:
        while line := f.readline():
            if line == "\n":
                flag += 1
                continue

            if flag == END:
                flag = TAGS

            if flag == TAGS:
                line = "".join(filter(lambda c: c not in '[]"', line))
                tag, _, content = line.partition(" ")

            elif flag == MOVES:
                for s in line.split(" "):
                    ...


print(perf_counter() - t, len(games))
