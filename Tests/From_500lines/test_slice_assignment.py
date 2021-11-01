l = list(range(10))
l[3:8] = ["x"]
print(l)

l = list(range(10))
l[:8] = ["x"]
print(l)

l = list(range(10))
l[3:] = ["x"]
print(l)

l = list(range(10))
l[:] = ["x"]
print(l)
