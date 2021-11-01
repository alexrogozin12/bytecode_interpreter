class Thing(object):
    def foo(self):
        return 17


class SubThing(Thing):
    pass


st = SubThing()
print(st.foo())
