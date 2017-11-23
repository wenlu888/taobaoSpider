from itertools import combinations

def get_list():
    s = [{"miumiu":1},{"lingling":2},{"lulu":3}]
    for i in range(1,len(s)+1):
        a = list(combinations(s,i))
        print a

def list1():
    s = [[1,"miumiu"],[2,"lingling"],[3,"lulu"]]
    '''
    for i in range(1,len(s)):
        a = combinations(s,i)
        while True:
            b = a.next()
            print b
    '''
    for i in combinations(s,2):
        print i


def get_zero():
    L = [2,8,3,50]
    z = 1
    count = 0
    for l in L:
        z = z*l

    for i in range(1,len(str(z))):
        if str(z)[-i] == "0":
            count += 1
    print count


if __name__ == '__main__':
    #get_list()
    #list1()
    get_zero()