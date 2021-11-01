def make_adder(x):
    def add(y):
        return x + y

    return add


a = make_adder(10)
print(a(7))
assert a(7) == 17
