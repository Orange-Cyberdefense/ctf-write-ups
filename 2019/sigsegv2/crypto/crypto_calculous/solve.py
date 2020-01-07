#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math,timeit
from sympy.ntheory import factorint
from sympy.ntheory.residue_ntheory import discrete_log
from sympy.ntheory.generate import primerange
import numpy as np
from copy import deepcopy
from itertools import combinations
import random
import time
import sys
from sacricat.client import Server, logging

N = 1

def rev_dict(d):
    new_dict = {}
    for k,v in d.items():
        if v in new_dict:
            new_dict[v].append(k)
        else:
            new_dict[v] = [k]
    return new_dict

def randint_by_corpus():
    keys = list(Number.corpus_i.keys())
    quo = random.choice(keys)
    rest = random.choice(keys)
    n = (quo * N + rest)
    p = random.randint(0,50)
    return n,p


class Number(int):
    corpus_i = {}
    corpus_s = {}

    @classmethod
    def reset(cls):
        cls.corpus_i = {}
        cls.corpus_s = {}

    @classmethod
    def get_number(cls,squo_factors,srest_factors):
        def _get_number(sfactors):
            number = 1
            for factor, factor_pow in sfactors.items():
                number *= cls.corpus_s[factor] ** factor_pow
            return number
        quo = _get_number(squo_factors)
        rest = _get_number(srest_factors)
        return int(quo * N + rest)

    @classmethod
    def get(cls,obj):
        if type(obj) in [int,np.int64] :
            if obj > N:
                quo,rest = Number.get_repr(obj)
                if quo and rest:
                    return cls.corpus_i[quo], cls.corpus_i[rest]
                if quo:
                    return cls.corpus_i[quo], None
                if rest:
                    return None, cls.corpus_i[rest]
                else :
                    return None, None
            elif obj in cls.corpus_i:
                return cls.corpus_i[obj]
            else:
                return None
        elif type(obj) in [str,np.str_]:
            if "_et_" in obj:
                squo,srest = obj.split("_et_")
                if squo and srest:
                    return cls.corpus_s[squo], cls.corpus_s[srest]
                elif squo:
                    return cls.corpus_s[squo], None
                elif srest:
                    return None, cls.corpus_s[srest]
                else:
                    return None, None 
            elif obj in cls.corpus_s:
                return cls.corpus_s[obj]
            else:
                return None
        else:
            print("Unknown type in Number.get :"+str(obj)+" "+str(type(obj)))
        return None

    @classmethod
    def add(cls,i,s):
        print("add :",i,s)
        cls.corpus_i[i] = s
        cls.corpus_s[s] = i

    @classmethod
    def get_repr(cls,obj):
        if type(obj) in [int,np.int64] :
            if obj > N:
                return obj // N, obj % N
            return obj
        elif type(obj) in [str,np.str_]:
            if "_et_" in obj:
                squo,srest = obj.split("_et_")
                return squo,srest
            else:
                return obj
        else:
            print("Unknown type in Number.get_repr :"+str(obj)+" "+str(type(obj)))
        return None

    def __contains__(self,obj):
        if type(obj) in [int,np.int64] :
            if obj < N:
                return obj in self.corpus_i
            else:
                return (obj // N in Number() and obj % N in Number())
        elif type(obj) in [str,np.str_]:
            if "_et_" not in obj:
                return obj in self.corpus_s 
            else:
                squo,srest = obj.split("_et_")
                return (squo in Number() and rest in Number())
        elif type(obj) is dict:
            keys = list(obj)
            for key in keys:
                if key not in Number():
                    return None
            return True
        else:
            print("Unknown type in Number.__contains__ :"+str(obj)+" "+str(type(obj)))
            sys.exit(0)
        return None

    def to_s(self):
        if self < N:
            return self.corpus_i[self]
        return str(self)

    def to_i(self,string):
        return self.corpus_s[string]

class SubCorpus():
    subcorpus = []

    @classmethod
    def compare(cls):
        changed = True
        while changed:
            changed = False
            list_corpus = deepcopy(cls.subcorpus)
            new_corpus = []

            for corpus, corpus2 in combinations(list_corpus,2):
                factor_pows = list(corpus.factors.keys())
                factor_pows2 = list(corpus2.factors.keys())

                for factor_pow in factor_pows:
                    if not (factor_pow in corpus.factors and factor_pow in corpus2.factors):
                        continue
                    intersection = list(np.intersect1d(corpus.factors[factor_pow],corpus2.factors[factor_pow]))
                    intersection.sort()
                    sintersection = list(np.intersect1d(corpus.sfactors[factor_pow],corpus2.sfactors[factor_pow]))
                    sintersection.sort()
                    if len(intersection) == 0 or \
                        (len(intersection) == len(corpus.factors[factor_pow]) and len(intersection) == len(corpus2.factors[factor_pow])):
                        # Here intersection is empty or full so we can't deduce anything.
                        if corpus not in new_corpus:
                            new_corpus.append(corpus)
                        if corpus2 not in new_corpus:
                            new_corpus.append(corpus2)
                    elif len(intersection) == 1:
                        # Only one element in the intersection, so we can deduce 1 number from it.
                        changed = True
                        Number.add(intersection[0],sintersection[0])

                        # Remove the corpus from the list to be processed
                        # because we're gonna change them
                        if corpus in new_corpus:
                            new_corpus.remove(corpus)
                        if corpus2 in new_corpus:
                            new_corpus.remove(corpus2)
                        
                        # Removal of the element added to our general corpus
                        corpus.factors[factor_pow].remove(intersection[0])
                        corpus.sfactors[factor_pow].remove(sintersection[0])

                        # Let's check the first corpus, if it's useful to process it again.
                        if corpus.verify() and corpus not in new_corpus:
                            new_corpus.append(corpus)

                        # Removal of the element added to our general corpus
                        corpus2.factors[factor_pow].remove(intersection[0])
                        corpus2.sfactors[factor_pow].remove(sintersection[0])

                        # Let's check the second corpus, if it's useful to process it again.
                        if corpus2.verify() and corpus2 not in new_corpus:
                            new_corpus.append(corpus2)
                        
                    elif len(intersection) > 1:
                        # There are several elements in the intersection
                        # Xor can give us something more to know
                        # Potentially another number with the xor of the 2 corpus
                        changed = True
                        xor = list(np.setxor1d(corpus.factors[factor_pow],corpus2.factors[factor_pow]))
                        xor.sort()
                        sxor = list(np.setxor1d(corpus.sfactors[factor_pow],corpus2.sfactors[factor_pow]))
                        sxor.sort()

                        # We delete the 2 corpus, because we will add the intersection and their xor
                        if corpus in new_corpus:
                            new_corpus.remove(corpus)
                        if corpus2 in new_corpus:
                            new_corpus.remove(corpus2)

                        if len(xor) == 1:
                            # if the xor returns a single element then we add it to the general corpus
                            Number.add(xor[0],sxor[0])
                        else:
                            # otherwise you have to consider the corpus of xor
                            c_xor = SubCorpus({factor_pow:xor},{factor_pow:sxor},False)
                            if c_xor and c_xor not in new_corpus:
                                new_corpus.append(c_xor)
                        # Add the corpus of the intersection
                        c_inter = SubCorpus({factor_pow:intersection},{factor_pow:sintersection},False)
                        if c_inter and c_inter not in new_corpus:
                            new_corpus.append(c_inter)
            if new_corpus:
                # If the new_corpus is not empty then we update our list of sub-corpuses
                for index in range(len(new_corpus)-1,-1,-1):
                    if not new_corpus[index]:
                        new_corpus.pop(index)
                cls.subcorpus = new_corpus
        return new_corpus

    def __init__(self,factors, sfactors,add=True):
        skeys = list(sfactors.keys())
        if type(skeys[0]) == str:
            self.factors = rev_dict(factors)
            self.sfactors = rev_dict(sfactors)
        else:
            self.factors = factors
            self.sfactors = sfactors

        for k in self.factors:
            self.factors[k].sort()
        for k in self.sfactors:
            self.sfactors[k].sort()

        self._add = add
        self.validated = self.verify()

        if self.validated and self._add:
            self.subcorpus.append(self)
            self.compare()

    def __str__(self):
        return "<factor:"+str(self.factors)+",sfactor:"+str(self.sfactors)+">"

    def __repr__(self):
        return "<factor:"+str(self.factors)+",sfactor:"+str(self.sfactors)+">"

    def __eq__(self,other):
        if isinstance(other,self.__class__):
            return (self.factors == other.factors and self.sfactors == other.sfactors)
        return False

    def __bool__(self):
        return self.validated

    def _len(self):
        length = 0
        for k in self.factors:
            length += len(self.factors[k])
        print("length :",self,length)
        return length

    def _verify_element_under_N(self,factor_pow,factors,sfactors):
        changed = False
        # Check for duplicates
        for fl in [factors,sfactors]:
            for index in range(len(fl)-1,-1,-1):
                factor = fl[index]
                if factor in Number():
                    if type(factor) is int:
                        self.factors[factor_pow].remove(factor)
                    else:
                        self.sfactors[factor_pow].remove(factor)
                    fl.pop(index)
                    changed = True

        if len(factors) == 1 and factors[0] not in Number():
            # If there's only one thing left, then we know what it is.
            Number.add(factors[0],sfactors[0])
            self.factors[factor_pow].remove(factors[0])
            self.sfactors[factor_pow].remove(sfactors[0])
            changed = True
        elif len(self.factors[factor_pow]) == 0:
            # If there is no longer a factor for the given power then
            # the empty factor table for the given power is deleted
            self.factors.pop(factor_pow)
            self.sfactors.pop(factor_pow)
            changed = True
        return changed

    def _verify_element_upper_N(self,factor_pow,factors,sfactors):
        changed = False
        # Check for duplicates and known partial values 
        for index in range(len(factors)-1,-1,-1):
            factor = factors[index]
            quo, rest = Number.get_repr(factor)
            squo = Number.get(quo)
            srest = Number.get(rest)
            if squo and srest:
                # It's a duplicate
                self.factors[factor_pow].remove(factor)
                factors.pop(index)
                changed = True
            elif squo or rest:
                # The quotient is known, let's see if we can deduce the rest.
                potential_sfactors = [sf for sf in sfactors if squo in sfactors]
                # If there's only one, then it's all right, we know the rest.
                # Otherwise you can't know yet without dealing with other values.
                # So we'll go back to the verification function, because we're going to modify the corpus.
                if len(potential_sfactors) == 1:
                    Number.add(rest,srest)
                    self.factors[factor_pow].remove(factor)
                    self.sfactors[factor_pow].remove(factor)
                    changed = True
            elif srest:
                # The rest is known, let's see if we can deduce the quotient
                potential_sfactors = [sf for sf in sfactors if srest in sfactors]
                # If there's only one, then it's all right, we know the quotient.
                # Otherwise you can't know yet without dealing with other values.
                # So we'll go back to the verification function, because we're going to modify the corpus.
                if len(potential_sfactors) == 1:
                    Number.add(quo,squo)
                    self.factors[factor_pow].remove(factor)
                    self.sfactors[factor_pow].remove(factor)
                    changed = True


        if len(factors) == 1:
            # If there's only one thing left then we know it
            quo,rest = Number.get_repr(factors[0])
            squo,srest = sfactors[0].split('_et_')
            if quo not in Number():
                Number.add(quo,squo)
            if rest not in Number():
                Number.add(rest,srest)
            self.factors[factor_pow].remove(factors[0])
            self.sfactors[factor_pow].remove(sfactors[0])
            if quo in self.factors[factor_pow]: self.factors[factor_pow].remove(quo)
            if rest in self.factors[factor_pow]: self.factors[factor_pow].remove(rest)
            if squo in self.sfactors[factor_pow]: self.sfactors[factor_pow].remove(squo)
            if srest in self.sfactors[factor_pow]: self.sfactors[factor_pow].remove(srest)
            return True
        elif factor_pow in self.factors and len(self.factors[factor_pow]) == 0:
            # If there is no longer a factor for the given power then
            # the empty factor table for the given power is deleted
            self.factors.pop(factor_pow)
            self.sfactors.pop(factor_pow)
            return True

    def verify(self):
        factor_pows = list(self.factors.keys())
        for factor_pow in factor_pows:
            changed = True
            while changed and factor_pow in self.factors:
                changed = False
                if len(self.factors) == 0:
                    # As the subcorpus is empty, it is not validated.
                    self.validated = False
                    return False

                # We treat the elements according to their position against N
                factors_under_N = [f for f in self.factors[factor_pow] if f < N]
                sfactors_under_N = [f for f in self.sfactors[factor_pow] if "_et_" not in f]
                factors_upper_N = [f for f in self.factors[factor_pow] if f >= N]
                sfactors_upper_N = [f for f in self.sfactors[factor_pow] if "_et_" in f]

                changed = self._verify_element_under_N(factor_pow,factors_under_N,sfactors_under_N)
                
                if self._verify_element_upper_N(factor_pow,factors_upper_N,sfactors_upper_N):
                    changed = True
        # The subcorpus is validated
        self.validated = True
        return True

def fill_corpus(number,string,n=N):
    quo,rest = Number.get_repr(number)
    string = string.split('_et_')
    if len(string) == 2:
        Number.add(quo,string[0])
        Number.add(rest,string[1])
    else:
        Number.add(quo,string[0])

    return quo,rest

def get_factors(number,po):
    client.sendLine("1")
    client.recvUntil("(ligne vide pour finir)\n")
    line = number

    if type(number) == int or type(number) == np.int64:
        number = int(number)
        quo, rest = Number.get(number)
        line = quo
        if rest:
            line += "_et_"+rest

    line += "-"+str(po)
    client.sendLine(line)
    client.sendLine()
    resp = client.recvUntil("[.] 3 - Quitter\n")
    if type(resp) is not str:
        resp = resp.decode('utf8')
    resp = resp.split('Quoi faire ?')[0].strip().split('\n')[-1].split(' = ')

    if len(resp) == 2:
        resp = resp[1].strip()
        factors = {factor.split('^')[0].strip() : int(factor.split('^')[1].strip()) for factor in resp.split('*')}
        return factors
    return None

def do_number(number,po=1):
    pow_number = pow(int(number),po, p)
    factors = factorint(pow_number)
    sfactors = get_factors(number,po)

    if sfactors:
        s = SubCorpus(factors,sfactors)

def check_corpus(a_quo_sfactors,a_rest_sfactors,b_quo_sfactors,b_rest_sfactors):
    if a_quo_sfactors in Number() and \
        a_rest_sfactors in Number() and \
        b_quo_sfactors in Number() and \
        b_rest_sfactors in Number():
        return True
    return False

while 1:
    N = 4500 # level 1
    N =200000 # Level 2
    NB_REQUESTS = 500
    
    Number.reset()
    primes_N = primerange(0,N)
    
    # Your socket librairy
    # client = Server('finale-challs.rtfm.re',5557)# level 2
    # client = Server('finale-challs.rtfm.re',5555)# level 1
    client = Server('127.0.0.1',4242,logLevel=logging.DEBUG) # local test
    
    resp = client.recvUntil("[.] 3 - Quitter\n")
    # resp = resp.decode('utf-8')
    resp = resp.split('\n')
    
    for r in resp:
        if "tu pourras rentrer lignes par ligne des expressions comme" in r:
            resp_first = r.split(' ')[-1][:-2]
        if "L'expression indiquée correspond à un nombre entre 2 et " in r:
            p = int(r.split(',')[0].split('et ')[1])+1
        if "Combien de" in r:
            A = r.split(' y a-t-il dans ')[0].split("Combien de ")[1].strip()
            B = r.split(' y a-t-il dans ')[1].split("?")[0].strip()
    print("P :",p," Challenge :",A,"dans",B,"?")

    try:
        a_quo_sfactors = get_factors(A.split("_et_")[0],1)
        a_rest_sfactors = get_factors(A.split("_et_")[1],1)
        b_quo_sfactors = get_factors(B.split("_et_")[0],1)
        b_rest_sfactors = get_factors(B.split("_et_")[1],1)
    except Exception as e:
        print(e)
        # For N = 200 000, there's less chance of quickly finding
        # the translation of the numbers into the primary factors
        # If there is only the quotient, the probability that it is > 20000 is very high.
        client.close()
        continue

    first = 4500*3256+1829
    quo, rest = fill_corpus(first,resp_first)
    do_number(first)

    iteration = 1

    while not check_corpus(a_quo_sfactors,a_rest_sfactors,b_quo_sfactors,b_rest_sfactors) and iteration < NB_REQUESTS:
        i = 1
        prime = next(primes_N)
        print("test",prime)
        while prime in Number():
            prime = next(primes_N)
        while (prime * (i)) < p:
            try:
                power = discrete_log(p,prime*i,first)
                break
            except Exception as e:
                i += 1
                continue
        if power:
            iteration += 1
            print("iteration :",iteration,"for",prime,end=" | ")
            do_number(first,power)

    print("nb corpus elts :",len(Number.corpus_i),"nb iteration :",iteration)
    print("P :",p," Challenge :",A,"dans",B,"?")
    if check_corpus(a_quo_sfactors,a_rest_sfactors,b_quo_sfactors,b_rest_sfactors):
        A = Number.get_number(a_quo_sfactors,a_rest_sfactors)
        B = Number.get_number(b_quo_sfactors,b_rest_sfactors)

        sol = discrete_log(p,B,A)
        print("A et B:",A,B," sol:",sol)

        client.sendLine("2")
        client.recv(512)
        client.sendLine(str(sol))
        resp = client.recv(512)
        print(resp)
        client.close()
        if "tiens le flag pour toi" in resp:
            sys.exit(0)

# b'Bien jou\xc3\xa9, tiens le flag pour toi: sigsegv{0mg_but_did_u_re4ll1_ind3x_C4lculused_th3_CH411_0r_ch3413D?}\n'
# b'Bien jou\xc3\xa9, tiens le flag pour toi: sigsegv{H4rD_t1m3_f0r_Z/PZ_t0_B3_iS0m0rph1sm3D}\n'
