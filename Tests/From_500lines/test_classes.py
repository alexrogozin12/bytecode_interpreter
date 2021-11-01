class Thing(object):
    def __init__(self, x):
        self.x = x

    def meth(self, y):
        return self.x * y


thing1 = Thing(2)
thing2 = Thing(3)
print(thing1.x, thing2.x)
print(thing1.meth(4), thing2.meth(5))
