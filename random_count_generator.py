import random


def roulette(dist):
    thres = random.random()
    i = 0
    for p in dist.items():
       i += p[1]
       if i >= thres:
           return p[0]

def random_count_generator():
    p = {1:0.5, 2:0.25, 3:0.15, 4:.05, 5:0.05}
    return roulette(p)

def rng_to_console():
    while(1):
        input('press <ENTER> to see random number.')
        print(random_count_generator())

if __name__=='__main__':
    rng_to_console()
