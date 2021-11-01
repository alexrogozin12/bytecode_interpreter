def make_adder(x):
    z = x + 1

    def add(y):
        return x + y + z

    return add


a = make_adder(10)
print(a(7))
assert a(7) == 28
