#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

ciphertext = '0dede85ca916c63e83eefb630ff1c6802fd38478eb62683ce9b69763dbafca80'
c = ['68636d62627672786f626e656e616771',
     '6870666a7a796f6c67737477696c6772',
     '63796a7476616a72676a7373796f6969',
     '786d696578756963796971616e6d787a',
     '6777766d6e747571656a656b667a6c75',
     '7a6b6c6a636c6f6972747a7371636d65',
     '6f6c7376747a737471637a636e61796d',
     '686e6c746266686b7a6b796c707a6c66',
     '7476646b646a78677571656561726c79',
     '757974736a756165706f747472627479',
     '6c6e6c696d6e70767a72737565766973',
     '6a787a727465756e7362637374747368']
r =  [97, 115, 27, 44, 92, 55, 27, 73, 120, 13, 112, 1]

new_c = []
for vc in c:
    new_vc = []
    for i in range(0,len(vc),2):
        for b in bin(int(vc[i:i+2],16))[2:].zfill(8):
            new_vc.append(int(b,2))
    new_c.append(new_vc)
c = new_c

def simplifyXor(equation,mult=False):
    operands = list(set(equation.split('^')))
    operands.sort()
    dict_operand = {}
    for operand in operands:
        count = len(re.findall('(?=\^%s\^)'%operand.replace('[','\[').replace(']','\]').replace('*','\*'),equation))
        count += len(re.findall('(?=^%s\^)'%operand.replace('[','\[').replace(']','\]').replace('*','\*'),equation))
        count += len(re.findall('(?=\^%s$)'%operand.replace('[','\[').replace(']','\]').replace('*','\*'),equation))
        dict_operand[operand] = count % 2 # We are xorring, so we have to keep only the operands appearing an odd number of times.
    equation = ""
    xor_equation_value = 0
    for operand, count in dict_operand.items():
        if count == 1: # the operand must be kept
            if 'k' in operand or 'm' in operand:
                equation += "^"+operand
            else:
                xor_equation_value ^= int(operand) # the integers are xorred together to have more than one at the end (xor is commutative and associative)
    if xor_equation_value != 0:
        equation += "^"+str(xor_equation_value)
    equation = equation[1:]
    return equation


def sROTR(key,r):
    return key[-r:] +  key[:-r]

def sROTL(key,r):
    return key[r:] +  key[:r]

def sXor(a,b):
    res = []
    for i in range(len(a)):
        res.append(simplifyXor("%s^%s" % (a[i],b[i])))
    return res

def sRound_key(key,r):
    keys = [key]
    for i in range(1,12):
        if i % 2 == 1:
            keys.append(sROTR(keys[i-1],r[i-1]))
        else:
            keys.append(sROTL(keys[i-1],r[i-1]))
    return keys

def sEncrypt(plain,key,r,c):
    keys = sRound_key(key,r)
    print("--- round keys ---")
    print(len(keys))
    for k in keys:
        print(k)
    cipher = plain
    for i in range(11):
        print("--- Step",i,"---")
        cipher = sXor(cipher,keys[i])
        print("Xor  :",cipher)
        cipher = sROTR(cipher,r[i])
        print("Rotr :",cipher)
        cipher = sXor(cipher,c[i])
        print("Xor  :",cipher)
    cipher = sXor(cipher,keys[11])
    print("--- Encrypt :",cipher)
    return cipher

m = ["m%s" % i for i in range(128)]
k = ["k%s" % i for i in range(128)]

e = sEncrypt(m,k,r,c)

ciphertext = [int(ciphertext[i:i+2],16) for i in range(0,len(ciphertext),2)]

new_ciphertexts = []
for vc in [ciphertext[:16],ciphertext[16:]]:
    new_vc = []
    for i in vc:
        for b in bin(i)[2:].zfill(8):
            new_vc.append(int(b,2))
    new_ciphertexts.append(new_vc)
ciphertexts = new_ciphertexts

flag = ""
for ciphertext in ciphertexts:
    i = 0
    plain = ["_"]*128
    for equation in e:
        index = int(re.findall('m[0-9]+',equation)[0][1:])# message bit index
        plain[index] = ciphertext[i]
        if '^' in equation :
            plain[index] ^= int(equation.split('^')[1])
        i+=1
    ascii_plain = ""
    for i in range(0,len(plain),8):
        ascii_plain += chr(int("".join([str(p) for p in plain[i:i+8]]),2))
    flag += ascii_plain
print(flag)