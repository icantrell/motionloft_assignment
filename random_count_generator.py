import random
from queue import Queue
import bisect
import time

def roulette(dist):
    '''
    given probability dist creates generator.
    returns random number based on dist. 
    Time(log2(n))
    Space(n)
    '''
    wheel = []
    for p in dist.items():
        if wheel:
            wheel.append((p[1] + wheel[-1][0],p[0]))
        else:
            wheel.append((p[1],p[0]))
    while(1): 
        thres = random.random()
        try:
            yield wheel[bisect.bisect_right(wheel, (thres,))][1]
        except IndexError:
            yield wheel[-1][1]


class RNG():
    '''
    Random number generator class
    '''
    def __init__(self, p):
        '''
        input: probablity dist.
        '''
        self.p = p
        self.generator = roulette(p)
        #queue is a synchronized data structure.
        self.queue = Queue() 
         
    def generate(self):
        '''
        generates random number and remembers
        last 100 numbers.
        '''
        n = self.generator.__next__() 
        #pop one off the front if len=100
        if self.queue.qsize() == 100:
            self.queue.get()
        self.last = n
        self.queue.put(n)
        return n 

    def get_mapping(self, n):
        '''
        get the frequency of a number in the mapping
        '''
        if n not in self.p:
            print(str(n) + ' not in probability dist.')
            return None
        return self.p[n]
    
    def store_last(self, fname):
        try:
            f = open(fname, 'w')
            f.write(str(self.last) + ' ' + time.strftime('%m/%d/%Y::%H:%M:%S'))
            f.close()
            return True
        except AttributeError:
            print('No numbers have been generated yet.')
            return False
        except IOError:
            print('error opening file.')
            return False

def rng_to_console():
    '''
    loop to output rng numbers in console
    '''
    rng = RNG(p = {1:0.5, 2:0.25, 3:0.15, 4:0.05, 5:0.05})
    while(1):
        input('press <ENTER> to see random number.')
        print(rng.generate())

#if run as standalone.
if __name__=='__main__':
    rng_to_console()
