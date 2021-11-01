def make_adder(x, y=13, z=43):
    def add(q, r=11):
        return x + y + z + q + r

    return add


a = make_adder(10, 17)
print(a(7))
assert a(7) == 88
