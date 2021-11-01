def fact(n):
    if n <= 1:
        return 1
    else:
        return n * fact(n - 1)


f6 = fact(6)
print(f6)
assert f6 == 720
