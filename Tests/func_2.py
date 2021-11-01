def func_first(x):
    y = x or 4
    print(func_second(y))
    return -1


def func_second(z):
    print(123)
    return z // 5
