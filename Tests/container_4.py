a = 1
b = 123
c = 42 ** 4
d = 'gg'
st = set()

st.add(a)
st.update([b, c, d])
print(st)

new_st = set([b, c, a])
print(new_st.issubset(st))
print(st.issubset(new_st))
