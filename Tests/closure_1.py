def outer(x):
    def inner(y):
        return x + y
    return inner

func = outer(4)
print(func(5))

def wrapper(x, y=4):
    z = x ** 2
    print('z =', z)
    def result(z='hello'):
        print(x - 4, z * 2, y << 2)
    print('z =', z)
    return result

new_func = wrapper(1, 2)
new_func()
