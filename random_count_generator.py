import random
import bisect
import time
import threading
from queue import PriorityQueue, Queue

MAX_PQUEUE = 1000

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
            #in case rounding error causes thres to overshoot.
            yield wheel[-1][1]

class Writer(threading.Thread):
    '''Writing thread with synchronized priority queue.'''

    def __init__(self, fname):
        '''
        init Writer.
        '''
        super(Writer,self).__init__()
        self.fname = fname
        self.pqueue = PriorityQueue(MAX_PQUEUE) 
        self._stop_event = threading.Event()
        #keep a count of items in pqueue.
        self.n = 0
        #keep track of last item timestamp added to pqueue.
        self.last_time = time.time()

    def write(self, item):
        '''
        write to priority queue.
        '''
        self.pqueue.put(item) 
    
    def run(self):
        '''
        loop that writes whatever is in priority queue to file.
        '''
        while(1):

            #if no items in pqueue. The thread will hang here.
            item = self.pqueue.get()
            f = open(self.fname,'a')
            f.write(str(item[2]) + ' ' + item[1]+'\n')
            f.close()


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
        timestamp = time.time()
        localtime = time.strftime('%m/%d/%Y::%H:%M:%S') 
        return (timestamp,localtime,n)

    def get_mapping(self, n):
        '''
        get the frequency of a number in the mapping
        '''
        if n not in self.p:
            print(str(n) + ' not in probability dist.')
            return None
        return self.p[n]
    
    def store_last(self, fname):
        '''
        stores last generated number inside of file.
        '''
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


#if run as standalone.
if __name__=='__main__':
    rng = RNG(p = {1:0.5, 2:0.25, 3:0.15, 4:0.05, 5:0.05})
    writer= Writer('store.txt')
    writer.daemon = True
    writer.start()
    while(writer.isAlive()):
        writer.write(rng.generate())

