import random
from queue import Queue

def roulette(dist):
    '''
    given probability dist.
    returns random number based on dist. 
    '''
    thres = random.random()
    i = 0
    for p in dist.items():
       i += p[1]
       if i >= thres:
           return p[0]

class RNG():
    '''
    Random number generator class
    '''
    def __init__(self, p):
        '''
        input: probablity dist.
        '''
        self.p = p
        #queue is a synchronized data structure.
        self.queue = Queue() 
    
    def generate(self):
        '''
        generates random number and remembers
        last 100 numbers.
        '''
        freq = roulette(self.p)
        #pop one off the front if len=100
        if self.queue.qsize() == 100:
            self.queue.get()

        self.queue.put(freq)
        return freq

    def get_mapping(self, n):
        '''
        get the frequency of a number in the mapping
        '''
        if n not in self.p:
            print(str(n) + ' not in probability dist.')
            return None
        return self.p[n]

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
