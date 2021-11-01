def fn(a, b=17, c="Hello", d=[]):
    d.append(99)
    print(a, b, c, d)


fn(1)
fn(2, 3)
fn(3, c="Bye")
fn(4, d=["What?"])
fn(5, "b", "c")
