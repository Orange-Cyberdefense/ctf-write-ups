#!/usr/bin/env python3
# -*- coding: utf-8 -*-

client  = Server('finale-challs.rtfm.re',9002) # Your socket librairy
i = 0
pow2 = 2**2050

while True:
    i+=1
    resp = client.recvUntil('Give me d, p and q:')
    if "sigsegv{" in resp:
        print(resp)
        sys.exit(0)
    resp = resp.split('\n')
    N = int(resp[0].split(': ')[1])
    phi = int(resp[1].split(': ')[1])
    r = int(resp[2].split(': ')[1])
    e = 0x10001
    print("-- New turn --")
    print("N:",N,"phi:",phi,"r:",r)
    quo_N = N // pow2
            
    for i in range(10):
    	# Retrieve phi(p * q * r) = (p-1) * (q-1) * (r-1) et de d
        vrai_phi = (phi + ((quo_N-i)*2**2050))  
        if vrai_phi % (r-1) == 0:  
            d = Cryptodome.Util.number.inverse(0x10001, vrai_phi)
            break

    print("d:",d)
    n = N//r
    d_n = Cryptodome.Util.number.inverse(0x10001, vrai_phi//(r-1))
    p,q = factor_modulus(N//r,d_n,e)
    print("p:",p,"q:",q)
    client.sendLine("%s %s %s" % (d,p,q))