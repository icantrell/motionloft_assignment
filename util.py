import threading
import random
import bisect
import heapq
import time
import math
from queue import PriorityQueue


def roulette(dist, seed=0):
    '''
    given probability dist creates generator.
    returns random number based on dist.
    Time(log2(n))
    Space(n)
    '''
    r = random.Random()
    r.seed(seed)
    wheel = []
    for p in dist.items():
        if wheel:
            wheel.append((p[1] + wheel[-1][0],p[0]))
        else:
            wheel.append((p[1],p[0]))
    while(1):
        thres = r.random()
        try:
            yield wheel[bisect.bisect_right(wheel, (thres,))][1]
        except IndexError:
            #in case rounding error causes thres to overshoot return last.
            yield wheel[-1][1]

#monitor used to test threads
class PerformanceMonitor:
    sx= {}
    sxx= {}
    sn= {}
    sm = {}
    def __init__(self, ID):
        self.id = ID
        PerformanceMonitor.sx[ID] = 0
        PerformanceMonitor.sxx[ID] = 0
        PerformanceMonitor.sn[ID] = 0
        PerformanceMonitor.sm[ID] = 0

    def __enter__(self):
        self.t = time.time()

    def __exit__(self, type, value, traceback):
        t = time.time()
        PerformanceMonitor.sx[self.id] += t - self.t
        PerformanceMonitor.sxx[self.id] += (t - self.t)**2
        PerformanceMonitor.sn[self.id] += 1
        if PerformanceMonitor.sm[self.id] < t - self.t:
            PerformanceMonitor.sm[self.id] = t - self.t

    def get_max(ID):
        return PerformanceMonitor.sm[ID]

    def get_ave_time(ID):
        return PerformanceMonitor.sx[ID] / PerformanceMonitor.sn[ID]

    def get_sd(ID):
        '''
        get standard deviation adjusted for sampling.
        '''
        return math.sqrt((1/(PerformanceMonitor.sn[ID]))*PerformanceMonitor.sxx[ID] - ((1/(PerformanceMonitor.sn[ID]))*PerformanceMonitor.sx[ID])**2) * math.sqrt(PerformanceMonitor.sn[ID]/(PerformanceMonitor.sn[ID] - 1))

#init performance monitors
performance_monitors= {'rng insert':  PerformanceMonitor('rng insert'), 'writer write': PerformanceMonitor('writer write')}

class Observable:
    def __init__(self):
        super(Observable, self).__init__()
        self.subs = []

    def subcribe(self):
        raise NotImplementedError('Must implement subsrcibe.')

    def update_subscribe(self):
        raise NotImplementedError('Must implement update_subscribe.')

class Observer:
    def observe(self):
        raise NotImplementedError('Must implment observe.')
    
    
class PQueueItem:
    '''
    Container that makes it so that the priority queue entry, including the random number itself,
    is not compared. Since only the time it was made should be in the comparison.
    '''
    def __init__(self, item, key):
        self.item = item
        self.key = key

    def __lt__(self, oitem):
        return self.item[self.key] <= oitem[self.key]

    def __getitem__(self, key):
        return self.item[key]

#link to library source
#https://hg.python.org/cpython/file/tip/Lib/queue.py
class PQueue(PriorityQueue):
    def __init__(self, maxsize = 0, number_producers = 0):
        super(PQueue, self).__init__(maxsize)
        self.num_p= number_producers

    #modified get function from python source code.
    def peek(self, block = True, timeout = None):
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self.queue[0]
            return item
    
    def get_queue(self, block = True, timeout = None):
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self.queue
            return item

    def put(self, item, block=True, timeout=None):
        '''Put an item into the queue.

       	Blocks after item is inserted and queue is about to be full.
	!!-Important since it keeps the generators from making an item while the queue is blocked-!!!
	'''
        with self.not_full:
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

            if self.maxsize > 0  + self.num_p:
                if not block:
                    if self._qsize() >= self.maxsize- self.num_p:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize- self.num_p:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize- self.num_p:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
