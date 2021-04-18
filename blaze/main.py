import sys
from primitives import primitives as prim
from protocols import protocols
from config import config as conf
import numpy as np

def main():
	conf.partyNum = int(sys.argv[1])
	print("*******SERVER ", conf.partyNum, end="*******\n")
	if conf.partyNum == 0:
		conf.PORT = 8004
		conf.advPORT_1 = 8005
		conf.advPORT_2 = 8006
	elif conf.partyNum == 1: 
		conf.PORT = 8005
		conf.advPORT_1 = 8004
		conf.advPORT_2 = 8006
	elif conf.partyNum == 2:
		conf.PORT = 8006
		conf.advPORT_1 = 8004
		conf.advPORT_2 = 8005
	else:
		print("Need a valid server number as a command line argument!")
		exit()



if __name__ == '__main__':
	main()