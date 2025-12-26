p='tools/listings.py'
with open(p,'rb') as f:
    s=f.read()
print('len',len(s))
print('""" count', s.count(b'"""'))
print("''' count", s.count(b"'''"))
