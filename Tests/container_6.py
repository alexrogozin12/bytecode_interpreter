a = [1, 2]
b = [3, 4]
c = [5, 6]
unpacked = [*a, *b, *c]
unpacked += [*c]
print(unpacked)
