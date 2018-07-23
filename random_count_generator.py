import time
import threading
from util import roulette, PerformanceMonitor, PQueue, PQueueItem, Observable, Observer, performance_monitors

MAX_PQUEUE = 100 
QUEUE_WAIT_TIME = 0.05
PRODUCERS = 5

class Writer(threading.Thread, Observer):
    '''Writing thread with synchronized priority queue.'''

    def __init__(self, fname):
        '''
        init Writer.
        '''
        super(Writer,self).__init__()
        self.fname = fname
        self.pqueue = PQueue(MAX_PQUEUE, PRODUCERS) 
        #keep a count of items in pqueue.
        self.n = 0
        #keep track of last item timestamp added to pqueue.
        self.last_time = time.time()
        self._stop_event = threading.Event()

    def observe(self, item):
        '''
        write to priority queue.
        '''
        #will block thread if queue is full.
        self.pqueue.put(item) 
    
    def run(self):
        '''
        loop that writes whatever is in priority queue to file.

        '''
        self.write_file = open(self.fname,'a')
        while(not self._stop_event.is_set()): 
            #test if oldest item has been in the queue long enough for others to be inserted.  
            t= self.pqueue.peek()['timestamp']
            if time.time() - t > QUEUE_WAIT_TIME: 
                with performance_monitors['writer write']:
                    #pop and write item.
                    item = self.pqueue.get()
                    #used to debug threads
                    #self.write_file.write(str(item['number'])  +  ' ' + str(item['timestamp'])+ ' ' + str(item['thread id'])+'\n')
                    self.write_file.write(str(item['number']) + ' ' + str(item['timestamp'])+'\n') 

    def stop(self):
        self._stop_event.set()
        #let stuff in queue get written before closing file.
        time.sleep(QUEUE_WAIT_TIME*10)
        self.write_file.close()
            

class RNG(Observable, threading.Thread):
    '''
    Random number generator class
    '''
    def __init__(self, p,seed=0):
        '''
        input: probablity dist.
        '''
        #init thread
        super(RNG,self).__init__()
        self.p = p
        self.generator = roulette(p,seed)
        #queue is a synchronized data structure.
        self._stop_event = threading.Event()

         
    def generate(self):
        '''
        generates random number and remembers
        last 100 numbers.
        '''
        n = self.generator.__next__() 
        localtime = time.time() 
        item =  PQueueItem(item = {'timestamp':localtime,'thread id':threading.get_ident(),'number':n}, key = 'timestamp')
        #pop one off the front if len=100
        self.last = item
        return item 

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
            f.write(str(self.last['number']) + ' ' + str(self.last['timestamp'])+'\n')
            f.close()
            return True
        except AttributeError:
            print('No numbers have been generated yet.')
            return False
        except IOError:
            print('error opening file.')
            return False

    def run(self):
        '''
        generates numbers and feeds to subscribed writer/s.
        '''
        while(not self._stop_event.is_set()):
            #test performance to make sure priority and timers are big and long enough.
            with performance_monitors['rng insert']:
                self.generate()
                self.update_subs()

    def update_subs(self):
        for sub in self.subs:
            sub.observe(self.generate())
    
    def subscribe(self, observer):
        self.subs.append(observer)

    def stop(self):
        self._stop_event.set()

#if run as standalone.
if __name__=='__main__':
    p = {1:0.5, 2:0.25, 3:0.15, 4:0.05, 5:0.05}
    #clear file
    open('store.txt','w').close()
    writer= Writer('store.txt')
    writer.daemon = True
    writer.start()
    
    rngs = []
    for i in range(PRODUCERS): 
        rng = RNG(p,seed = i)
        rngs.append(rng)
        #point rngs to write to writer.
        rng.subscribe(writer)
        rng.daemon = True
        #start rngs to generate numbers for 10 seconds.
        rng.start()
    
    print('generating numbers...')
    time.sleep(10) 
    
        

