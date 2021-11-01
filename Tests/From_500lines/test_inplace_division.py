x, y = 24, 3
x /= y
assert x == 8.0 and y == 3
assert isinstance(x, float)
x /= y
assert x == (8.0 / 3.0) and y == 3
assert isinstance(x, float)
