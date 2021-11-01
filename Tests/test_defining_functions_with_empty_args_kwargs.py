def fn(*args):
    print("args is %r" % (args,))


fn()


def fn(**kwargs):
    print("kwargs is %r" % (kwargs,))


fn()


def fn(*args, **kwargs):
    print("args is %r, kwargs is %r" % (args, kwargs))


fn()
