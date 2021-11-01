def f(a, b):
    return not (a and b)


assert f(17, 0) is True
assert f(0, 23) is True
assert f(0, "") is True
assert f(17, 23) is False
