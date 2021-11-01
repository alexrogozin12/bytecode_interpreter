def func(x: "annot 1", y: "annot 2" = 4, *, z=5):
    return x ** 2 + y - z


print(func(4), func(7, z=4), func(x=1, y=81, z=7))
print('x' in func.__annotations__)
print('hello' in func.__annotations__)
print('annot 1' in func.__annotations__.values())
