import sys
from primitives import primitives as prim
from protocols import protocols
from shares import angular_shares as ang
from shares import special_shares as spc
from config import config as conf
import numpy as np

def main():
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

	a = spc()
	b = spc()

	if(conf.PRIMARY):
		a.x1 = 1
		a.x2 = 8192 + 2
		a.x3 = 2

	else:
		a.x1 = 1
		a.x2 = 1
		a.x3 = (8192 + 2) + 2

	c = protocols.multiplication(a,b)

	print("Share 0:",c.x1)
	print("Share 1:",c.x2)
	print("Share 2:",c.x3)

if __name__ == '__main__':
	main()