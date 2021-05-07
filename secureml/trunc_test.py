# ''''''''


import random
from gmpy2 import mpz

it = 100
l = 2**64
lx = 2**32
ld = 13
sum = 0 # sum of cases the truncation failed for in 500 rounds
count = 0
i=0

def split_shares(x,p,q):

    x_1 = mpz(random.randint(0, l-1))%(l)
    
    x_2 = mpz(x - x_1)%(l)

    return x_1,x_2

def int64tofloat(x,scale=1<<ld):
    y=0

    if(x > ((l/2) - 1)):
        x = (l) - x
        y = mpz(x) % (l)
        y = (y*mpz(-1))
    else:
        y = mpz(x) % (l)
        
    return float(y)/(scale)

def truncate(x,p,scale = 1<<ld):
        if(p==0):
            y = mpz(x) % (l)
        else:
            x = (l) - x
            y = mpz(x) % (l)
            y = (y*mpz(-1))

        return mpz(x)%(l)

while(i<it):
    i=i+1
    # print(i)
    x = mpz(random.randint(0, l-1))
    y = mpz(random.randint(0, l-1))
    # print(x)

    z = mpz(x*y)%(l)

    # if((z > lx and z < l - lx)):
    #     i = i-1
    #     continue

    trunc_z_1 = mpz(int64tofloat(z))%(l)

    z1,z2 = split_shares(z,1,1)

    # if((z1 > lx and z1 < l - lx) or (z2 > lx and z2 < l - lx)):
    #     i = i-1
    #     continue

    # Uncomment this to use SecureML's truncation
    t_z1 = truncate(z1,1<<ld,0)
    t_z2 = truncate(z2,1<<ld,1)

    # To use our truncation
    # t_z1 = mpz(int64tofloat(z1))%(l)
    # t_z2 = mpz(int64tofloat(z2))%(l)

    trunc_z_2 = mpz(t_z1+t_z2)%(l)

    if((trunc_z_1-trunc_z_2)==1 or (trunc_z_2-trunc_z_1)==1):
            count = count + 1

    try:
        # assert(trunc_z_1 == trunc_z_2)
        # print("hi")
        assert((trunc_z_1-trunc_z_2)==1 or (trunc_z_2-trunc_z_1)==1 or (trunc_z_1==trunc_z_2))
        print("Passed for the case below")
        print("x: ",x)
        print("y: ", y)
        print("z: ",z)
        print("z1: ",z1)
        print("z2: ",z2)
        print("truncation of whole z: ", trunc_z_1)
        print("t_z1: ", t_z1)
        print("t_z2: ", t_z2)
        print("truncation of the shares of z: ", trunc_z_2)
        print("\n")

    except:
        sum = sum + 1
        print("here")
        print("Failed for the case below")
        print("x: ",x)
        print("y: ", y)
        print("z: ",z)
        print("z1: ",z1)
        print("z2: ",z2)
        print("truncation of whole z: ", trunc_z_1)
        print("t_z1: ", t_z1)
        print("t_z2: ", t_z2)
        print("truncation of the shares of z: ", trunc_z_2)
        print("\n")

# print("Failed for "+str(count)+" cases!")

# print("sum: ", sum)
print("Fails for an average of "+str((sum*100.0)/it)+" percentage of time.")
# print(count/it)