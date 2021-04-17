#!/usr/bin/python
import sys
from config import config as conf
import socket
import pickle 
import random
import numpy as np
import math
import os

class primitives:

	def float2int(x): # embed float value onto the integer ring
		x = np.array(conf.converttoint64*(x), dtype = np.uint64)
		return x
	

	def int2float(x,scale=1<<conf.precision): # convert a value in the integer ring back to float
		y=0
		if(x > (2**(conf.l-1))-1):
			x = (2**conf.l) - x
			y = np.uint64(x)
			y = y*(-1)
		else:
			y = np.uint64(x)
			
		return float(y)/(scale)


	def send_val(send_info,send_IP,send_PORT): # send a value to another server and receive a value from the same server
		if(conf.partyNum == 0):
			ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			ssock.bind((conf.IP, conf.PORT))
			ssock.listen()
			while True:
				try:
					# print('Waiting for connection at : ',conf.IP,conf.PORT)
					client, addr = ssock.accept()
					# print('Received connection ')
					break
				except:
					continue

			recv_info = client.recv(4096)
			recv_info = pickle.loads(recv_info)
			client.send(pickle.dumps(send_info))
			client.close()
			ssock.close()
		else: 
			csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			while True:
				try:
					csock.connect((send_IP,send_PORT))
					# print("Connected")
					break
				except: 
					continue
			csock.send(pickle.dumps(send_info))
			recv_info = pickle.loads(csock.recv(4096))
			csock.close()

		return recv_info

	def send_val_2(send_info): # send a value to the other two servers and receive one value each from both of them
		
		recv_info_1 = send_val(send_val,conf.advIP_1,conf.advPORT_1)
		recv_info_2 = send_val(send_val,conf.advIP_2,conf.advPORT_2)

		return [recv_info_1,recv_info_2]

	def randsample_2(send_IP,send_PORT): # allow any two of the three parties to sample a random value together
		
		my_r = prim.float2int(random.uniform(-1*conf.max_dec,max_dec)) # sample a random float value from the possible range and embed it on the ring
		adv_r = send_val(my_r,send_IP,send_PORT)

		r = my_r + adv_r

		return r