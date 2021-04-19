import socket
# import numpy as np
# from primitives import primitives as prim

class config:

	partyNum = -1

	# IP = socket.gethostbyname(socket.gethostname())
	IP = '127.0.0.1'
	advIP_1 = IP
	advIP_2 = IP 
	
	PORT = -1
	advPORT_1 = -1
	advPORT_2 = -1

	PRIMARY = -1
	adv_party = -1

	ssock = -1
	csock1 = -1
	csock2 = -1
	client1 = -1
	client2 = -1
	
	l = 64
	lby2 = 32
	modl = 2**l
	max_dec = 0 # maximum positive decimal value possible to express in the integer ring

	precision = 13
	converttoint64 = (1<<precision)
	trunc_parameter = (1>>precision)
	
	epochs = 10
	
	blaze = 0
	thesis = 1

	MODE = blaze