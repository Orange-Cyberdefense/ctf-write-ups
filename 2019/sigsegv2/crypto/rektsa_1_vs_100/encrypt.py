#!/usr/bin/python2.7

import sys
from secret import FLAG
from Crypto.Util.number import getPrime, bytes_to_long
from gmpy2 import invert

for _ in range(100):
    p = getPrime(1024)
    q = getPrime(1024)
    r = getPrime(1028)

    e = 0x10001

    N = p * q * r
    phi = (p - 1) * (q - 1) * (r - 1)

    print 'N:', N
    print 'phi:', phi % 2**2050
    print 'r:', r

    print 'Give me d, p and q: '

    sys.stdout.flush()

    try:
        d, p, q = [int(inp) for inp in raw_input().split(' ')]
    except:
        print 'Invalid input!'
        exit(1)

    if d == invert(e, phi) and p * q * r == N:
        continue
    
    print 'Nope!'
    exit(1)

print 'Congratulations: %s' % FLAG
