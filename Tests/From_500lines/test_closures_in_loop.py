def make_fns(x):
    fns = []
    for i in range(x):
        fns.append(lambda i=i: i)
    return fns


fns = make_fns(3)
for f in fns:
    print(f())
assert (fns[0](), fns[1](), fns[2]()) == (0, 1, 2)
