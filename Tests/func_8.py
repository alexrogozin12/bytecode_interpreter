def my_func(x, y, z=5, w=4):
    x = z ** w
    y -= 2 * x + w - 3 * z
    print(x)


my_func(10, 20, 30, 40)
my_func(5, 6)
my_func(7, 99, z=19, w=5)
my_func(x=3, y=4, w=6, z=10)
