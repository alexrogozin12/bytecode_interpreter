def func(*args, z=4):
    'docstring'
    print(args, ' ', z)


func(1, 2, 3, 4, 'c')
func('hello ', 'world', z=6)
print(func.__doc__, func.__name__)