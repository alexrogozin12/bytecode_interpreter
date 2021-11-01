def func(x: "annot 1", y:"annot 2"=4, *, z=5):
    'nice wardy'
    return x ** 2 + y - z

print(func.__doc__)
print(func.__name__)
