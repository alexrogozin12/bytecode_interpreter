l = list(range(10))
del l[3:8]
print(l)

l = list(range(10))
del l[:8]
print(l)

l = list(range(10))
del l[3:]
print(l)

l = list(range(10))
del l[:]
print(l)

l = list(range(10))
del l[::2]
print(l)
