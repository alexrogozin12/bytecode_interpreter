a = {1: 'hello', 2: ' world'}
b = {3: ' nice', 2: ' to'}
c = {5: ' meet', 6: ' you'}
unpacked = {**a, **b, **c}
print(type(unpacked))
print(unpacked == {1: 'hello',
                   2: ' world',
                   3: ' nice',
                   4: ' to',
                   5: ' meet',
                   6: ' you'})
