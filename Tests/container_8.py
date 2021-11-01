a = ['hello', ' world']
b = [' nice', ' to']
c = (' meet', ' you')
unpacked = {*a, *b, *c}
print(unpacked, type(unpacked))
