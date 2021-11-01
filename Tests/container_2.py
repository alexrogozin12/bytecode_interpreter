lst = [1, 2, 3, 4, 5] + list(range(10))
st = set(lst)
a = 28
b = 4
c = 'hello'

for elem in [a, b, c]:
    if elem in st:
        print('elem in set')
    else:
        print('elem not in set')
