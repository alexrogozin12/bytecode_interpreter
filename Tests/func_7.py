a = [1, 2, 3]
b = [4, 5, 6, 'a', 'b', 'c']
c = [7, 8, 9, 'x', 'y', 'hello']
lists = [a, b, c]
for lst in lists:
    print(*lst, sep=', ', end='!\n')
