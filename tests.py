import random
import time 
import random_count_generator
from collections import Counter
from math import isclose
from util import roulette, PerformanceMonitor, PQueue, PQueueItem

def test_rng():
    rng = random_count_generator.RNG(p = {1:0.5, 2:0.25, 3:0.15, 4:0.05, 5:0.05})
    rng.daemon = True
    #test cannot store last item if none generated.
    assert(not rng.store_last('test_store.txt'))
    n = 1000000
    a = []
    for _ in range(n):
        a.append(rng.generate()['number'])

    assert(all(map(lambda x: isinstance(x,int),a)))
    
    #test frequencies. should succeed most of the time.
    c = Counter(a)
    assert(isclose(c[1]/n, 0.5, rel_tol=0.01)) 
    assert(isclose(c[2]/n, 0.25, rel_tol=0.01)) 
    assert(isclose(c[3]/n, 0.15, rel_tol=0.01)) 
    assert(isclose(c[4]/n, 0.05, rel_tol=0.01)) 
    assert(isclose(c[5]/n, 0.05, rel_tol=0.01)) 


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
    time.sleep(0.005)
    item2 = rng.generate()

    #entered into writer in reverse order.
    writer.observe(item2)
    writer.observe(item1)
    time.sleep(0.5)
    assert(writer.isAlive())
    writer.stop()
    time.sleep(0.5)

    lines = list(map( lambda x: x.strip(), open('test_test_store.txt','r').readlines()))
    assert(lines)
    #order of items is maintained by priority queue.
    x = (str(item1['number']) + ' ' + str(item1['timestamp']))
    assert(x == lines[0])
    x = (str(item2['number']) + ' ' + str(item2['timestamp']))
    assert(x == lines[1])

def test_bulk_write():
    rng = random_count_generator.RNG(p = {1:0.5, 2:0.25, 3:0.15, 4:0.05, 5:0.05})
    time.sleep(0.5)
    open('test_test_store.txt','w').close()
    writer= random_count_generator.Writer('test_test_store.txt')
    writer.daemon = True
    writer.start()
    for i in range(15):
        a =[]
        for _ in range(25):
            item = rng.generate()
            a.append(item)
            time.sleep(0.01)
        random.shuffle(a)
        for item in a:
            writer.observe(item)
        time.sleep(0.1)
    time.sleep(1.5)
    assert(writer.isAlive())
    writer.stop()
    lines = list(map( lambda x: x.split()[1], open('test_test_store.txt','r').readlines()))
    assert(lines)
    assert(all([lines[i] <= lines[i+1] for i in range(len(lines) -1)]))
    print(len(lines))


def test_performance():
    open('test_test_store.txt','w').close()
    writer= random_count_generator.Writer('test_test_store.txt')
    writer.daemon = True
    writer.start()

    a=[] 
    for _ in range(random_count_generator.PRODUCERS):
        rng = random_count_generator.RNG(p = {1:0.5, 2:0.25, 3:0.15, 4:0.05, 5:0.05})
        a.append(rng)
        rng.subscribe(writer)
        rng.daemon = True
        rng.start()
        
    time.sleep(15)
    for rng in a: 
        assert(rng.isAlive())
        rng.stop()
    assert(writer.isAlive())
    writer.stop()
        
    #measure how long it takes for rng thread to insert into priority queue.
    m0 = PerformanceMonitor.get_ave_time('rng insert')
    print('rng insert ave',m0)
    #2.790529960934435e-05
    m1 = PerformanceMonitor.get_ave_time('writer write')
    print('writer write', m1)

    max0 = PerformanceMonitor.get_max('rng insert')
    print('rng insert max',max0)
 
    sd0 = PerformanceMonitor.get_sd('rng insert')
    #8 standard deviations from the mean assures percentage that takes longer than lt is pretty much 0.(chance of number inserted in wrong order should be very roughly on order of e^-15)
    #0.0007253377875668702
    print('rng insert std',sd0)

    #largest possibly difference between two insert times that we should expect with high confidence statisically.
    ls = sd0 * 8  
    assert(random_count_generator.QUEUE_WAIT_TIME > ls)

        
    lines = list(map( lambda x: x.split()[1], open('test_test_store.txt','r').readlines()))
    assert(all([lines[i] <= lines[i+1] for i in range(len(lines) -1)]))
    assert(lines)
