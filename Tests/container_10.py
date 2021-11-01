def func(*args):
    summ = ''
    for arg in args:
        summ += arg
    return summ

a = ['hello', ' world']
b = [' nice', ' to']
c = (' meet', ' you')
print(func(*a, *b, *c))
unpacked = (*a, *b, *c)
print(func(*unpacked))
