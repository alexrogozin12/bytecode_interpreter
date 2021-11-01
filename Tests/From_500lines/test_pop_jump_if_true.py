def f(a):
    if not a:
        return 'foo'
    else:
        return 'bar'


assert f(0) == 'foo'
assert f(1) == 'bar'
