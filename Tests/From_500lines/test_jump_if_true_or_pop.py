def f(a, b):
    return a or b


assert f(17, 0) == 17
assert f(0, 23) == 23
assert f(0, "") == ""
