def my_func(x, *, y, z=5, w=4):
    x = z ** w
    y -= 2 * x + w - 3 * z
    print(x)

my_func(x=3, y=4, w=6, z=10)
my_func(3, y=4, w=6, z=15)
