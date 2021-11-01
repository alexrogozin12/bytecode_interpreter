def recur(x):
    if x < 0:
        return
    print(x)
    recur(x - 1)


recur(10)
