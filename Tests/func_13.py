def summ(multiplier, *args, **kwargs):
    res = 0
    # print(kwargs)
    for arg in args:
        res += arg
    for val in kwargs.values():
        res += val
    res *= multiplier
    return res


print(summ(2, 2, 3, 4, 5, x=4, y=2))
a = [1, 2, 3]
b = [4, 5, 6]
c = {'x': 7, 'y': 8, 'z': 9}
print(summ(*a, *b, **c))
# summ.example_attr = 'hello'
# summ.example_attr += ' world'
# print(summ.example_attr)
