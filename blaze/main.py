import sys
from primitives import primitives as prim
from protocols import protocols
from shares import angular_share as ang
from shares import special_share as spc
from config import config as conf
import numpy as np
from gmpy2 import mpz

def main():

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIGURE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
	
	conf.partyNum = int(sys.argv[1])
	print("*******SERVER ", conf.partyNum, end="*******\n")
	if conf.partyNum == 0:
		conf.PORT = 8004
		conf.advPORT_1 = 8005
		conf.advPORT_2 = 8006
		conf.PRIMARY = 0

	elif conf.partyNum == 1: 
		conf.PORT = 8005
		conf.advPORT_1 = 8004
		conf.advPORT_2 = 8006  
		conf.PRIMARY = 1

	elif conf.partyNum == 2:
		conf.PORT = 8006
		conf.advPORT_1 = 8004
		conf.advPORT_2 = 8005
		conf.PRIMARY = 1

	else:
		print("Need a valid server number as a command line argument!")
		exit()

	if(conf.PRIMARY):
		if(conf.partyNum == 1):
			conf.adv_party = 2 
		else:
			conf.adv_party = 1

	prim.connect()

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TEST BLAZE MULT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

	a = spc()
	b = spc()

	if(conf.PRIMARY):
		a.x1 = mpz(1)
		a.x2 = mpz(8191 + 2)
		a.x3 = mpz(2)

		b.x1 = mpz(1)
		b.x2 = mpz(8191 + 2)
		b.x3 = mpz(2)

	else:
		a.x1 = mpz(1)
		a.x2 = mpz(1)
		a.x3 = mpz((8191 + 2) + 2)

		b.x1 = mpz(1)
		b.x2 = mpz(1)
		b.x3 = mpz((8191 + 2) + 2)

	c = protocols.multiplication(a,b)

	# print(str(conf.partyNum)+" Share 0:",c.x1)
	# print(str(conf.partyNum)+" Share 1:",c.x2)
	# print(str(conf.partyNum)+" Share 2:",c.x3)


	if(conf.partyNum == 0):
		alp = (c.x1 + c.x2) % (conf.modl)
		# print("\n\nalpha: ",alp,end="\n")
		prim.send_val(alp,1)
		prim.send_val(alp,2)

	else:
		alp = prim.recv_val(0)
		v = (c.x2 - alp) % (conf.modl)

		print("Product: ",v)


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ TEST MULZK ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
	# a = ang()
	# b = ang()

	# if(conf.PRIMARY):
	# 	a.x1 = mpz(2)
	# 	a.x2 = mpz(8191) + mpz(2) + mpz(2)
	# 	# a.x3 = mpz(2)

	# 	b.x1 = mpz(2)
	# 	b.x2 = mpz(8191) + mpz(2) + mpz(2)
	# 	# b.x3 = mpz(2)

	# else:
	# 	a.x1 = mpz(2)
	# 	a.x2 = mpz(2)
	# 	# a.x3 = mpz((8191 + 2) + 2)

	# 	b.x1 = mpz(2)
	# 	b.x2 = mpz(2)
	# 	# b.x3 = mpz((8191 + 2) + 2)

	# c = protocols.mulZK(a,b)
	# print(str(conf.partyNum)+" Share 0:",c.x1)
	# print(str(conf.partyNum)+" Share 1:",c.x2)

	# if(conf.partyNum == 0):
	# 	alp = (c.x1 + c.x2) % (conf.modl)
	# 	print("\n\nalpha: ",alp,end="\n")
	# 	prim.send_val(alp,1)
	# 	prim.send_val(alp,2)

	# else:
	# 	alp = prim.recv_val(0)
	# 	v = (c.x2 - alp) % (conf.modl)

	# 	print("secret share: ",v)

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
	
	print("Server "+ str(conf.partyNum)+": Total number of bytes sent: "+str(conf.num_bytes_sent)+" bytes.")
	print("Server "+ str(conf.partyNum)+": Total number of bytes received: "+str(conf.num_bytes_received)+" bytes.")
	
	prim.disconnect()


if __name__ == '__main__':
	main()