def one():
    x = 1

    def two():
        x = 2
        print(x)

    two()
    print(x)


one()
