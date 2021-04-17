import socket
import numpy as np
from dataclasses import dataclass
# from primitives import primitives as prim

class config:

	partyNum = -1

	IP = socket.gethostbyname(socket.gethostname())
	advIP_1 = IP
	advIP_2 = IP 
	
	PORT = -1
	advPORT_1 = -1
	advPORT_2 = -1
	
	l = 64
	lby2 = 32
	modl = 2**l
	# max_dec = prim.int2float(2**(l-1)-1) # maximum positive decimal value possible to express in the integer ring

	precision = 13
	converttoint64 = (1<<precision)
	trunc_parameter = (1>>precision)
	
	epochs = 10
	
	blaze = 0
	thesis = 1

	MODE = blaze