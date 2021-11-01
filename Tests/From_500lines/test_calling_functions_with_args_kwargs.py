def fn(a, b=17, c="Hello", d=[]):
    d.append(99)
    print(a, b, c, d)


fn(6, *[77, 88])
fn(**{'c': 23, 'a': 7})
fn(6, *[77], **{'c': 23, 'd': [123]})
