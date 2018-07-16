import random_count_generator
from collections import Counter
from math import isclose

def test_rng():
    n = 10000000
    a = [random_count_generator.random_count_generator() for i in range(n)]

    c = Counter(a)
    assert(isclose(c[1]/n, 0.5, rel_tol=0.01)) 
    assert(isclose(c[2]/n, 0.25, rel_tol=0.01)) 
    assert(isclose(c[3]/n, 0.15, rel_tol=0.01)) 
    assert(isclose(c[4]/n, 0.05, rel_tol=0.01)) 
    assert(isclose(c[5]/n, 0.05, rel_tol=0.01)) 
