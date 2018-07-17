import time 
import random_count_generator
from collections import Counter
from math import isclose

def test_rng():
    rng = random_count_generator.RNG(p = {1:0.5, 2:0.25, 3:0.15, 4:0.05, 5:0.05})
    #test cannot store last item if none generated.
    assert(not rng.store_last('test_store.txt'))
    n = 1000000
    a = [rng.generate()[2] for i in range(n)]
    assert(all(map(lambda x: isinstance(x,int),a)))
    
    #test frequencies
    c = Counter(a)
    assert(isclose(c[1]/n, 0.5, rel_tol=0.01)) 
    assert(isclose(c[2]/n, 0.25, rel_tol=0.01)) 
    assert(isclose(c[3]/n, 0.15, rel_tol=0.01)) 
    assert(isclose(c[4]/n, 0.05, rel_tol=0.01)) 
    assert(isclose(c[5]/n, 0.05, rel_tol=0.01)) 

    assert(rng.queue.qsize() == 100)

    assert(rng.get_mapping(2) == 0.25)
    assert(rng.get_mapping(5) == 0.05)
    assert(rng.get_mapping(7) == None)

    assert(rng.store_last('test_store.txt'))
    assert(not rng.store_last('test_\nstore.txt'))

def test_writer():
    rng = random_count_generator.RNG(p = {1:0.5, 2:0.25, 3:0.15, 4:0.05, 5:0.05})
    open('test_test_store.txt','w').close()
    writer= random_count_generator.Writer('test_test_store.txt')
    writer.daemon = True
    writer.start()
    item1 = rng.generate()
    item2 = rng.generate()
    #let writer hang
    time.sleep(0.5)
    writer.write(item2)
    writer.write(item1)
    time.sleep(0.5)
    lines = list(map( lambda x: x.strip(), open('test_test_store.txt','r').readlines()))
    print(item1,item2)
    x = (str(item1[2]) + ' ' + item1[1])
    assert(x in lines)
    x = (str(item2[2]) + ' ' + item2[1])
    assert(x in lines)
    

    


