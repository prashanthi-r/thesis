import numpy as np
import math 

l = 64
scale = 1<<13

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# embed an array of float values into an array of integers in the integer ring

def floattoint64(x):
	x = np.array(scale*(x), dtype = np.uint64)
	return x

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# This function can be used for two purposes:
# 1. reverse embedding from the integer ring to float

def int64tofloat(x):
	y=0
	if(x > (2**(l-1))-1):
		x = (2**l) - x
		y = np.uint64(x)
		y = y*(-1)
	else:
		y = np.uint64(x)
		
	return float(y)/(scale)

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# Our truncation

def truncate(x):
	return np.uint64(int64tofloat(x))

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# The truncation function proposed in the SecureML paper.
# In our experiments, this function didn't work.

def truncate_secureml(x):
	if(conf.partyNum==0):
		x = x/scale
	else:
		x = (2**l) - x
		y = np.uint64(x)
		x = (y*(-1)/scale)
	return np.uint64(x)

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# split a value x into 2-out-of-2 additive secret shares

def split_shares(x,p=1,q=1):
	x_1 = np.uint64(np.random.uniform(0, (2**l), (p,q)))
	x_2 = np.subtract(x,x_1)%(2**l)
	return x_1,x_2

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def main():
	# x = 9.345
	# y = 16.456

	x = np.random.rand(1)
	y = np.random.rand(1)

	z = x*y
	z = z[0]
	print(z)

	# convert them from float to int64
	x1 = floattoint64(x)
	y1 = floattoint64(y)

	# multiply them
	z1 = (x1*y1)%(2**l)

	# create shares of the product
	a,b = split_shares(z1)

	# truncate a and b
	m = truncate(a)
	n = truncate(b) 

	# add m and n in modulo 2^64
	p = (np.add(m,n))%(2**l)

	# reverse map p
	z_dash = int64tofloat(p)

	assert(abs(float(z_dash - z))<=1)

	print(z_dash)

if __name__ == '__main__':
	# for i in range(100):
	main()		