#!/usr/bin/python
import sys
from config import config as conf
import socket
import pickle 
import random
import numpy as np
import math
import os
import hashlib

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

	def connect(): # connect all the servers with one another
		if(conf.PRIMARY):
			conf.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			conf.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			conf.ssock.bind((conf.IP, conf.PORT))
			conf.ssock.listen()

			if(conf.partyNum == 1):
				conf.csock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				while True:
					try:
						conf.csock1.connect((conf.advIP_2,conf.advPORT_2))
						print("Connected")
						break
					except: 
						continue

				while True:
					try:
						print('Waiting for connection at : ',conf.IP,conf.PORT)
						conf.client1, addr = conf.ssock.accept()
						print('Received connection ')
						break
					except:
						continue
			else:
				n_conn = 0
				while True:
					try:

						print('Waiting for connection at : ',conf.IP,conf.PORT)
						
						if(n_conn == 0):
							print("here")
							conf.client1, addr = conf.ssock.accept()
						else:
							conf.client2, addr = conf.ssock.accept()
						print('Received connection from',addr)

						n_conn = n_conn + 1

						if(n_conn == 2):
							break
					except:
						continue
		else:
			csock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			csock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			while True:
				try:
					conf.csock1.connect((conf.advIP_1,conf.advPORT_1))
					break
				except: 
					continue
			print("Connected")
			while True:
				try:
					conf.csock2.connect((conf.advIP_2,conf.advPORT_2))
					break
				except: 
					continue
			print("Connected")

	def disconnect():
		if(conf.partyNum == 1):
			conf.ssock.close()
			conf.csock1.close()
			conf.client1.close()

		elif(conf.partyNum == 2):
			conf.ssock.close()
			conf.client1.close()
			conf.client2.close()

		else:
			conf.csock1.close()
			conf.csock2.close()

	def send_recv_val(send_info,send_partyNum):
		if(conf.partyNum == 1):
			if(send_partyNum == 0):
				conf.client1.send(pickle.dumps(send_info))
				recv_info = conf.client1.recv(4096)
				recv_info = pickle.loads(recv_info)

			if(send_partyNum == 2):
				conf.csock1.send(pickle.dumps(send_info))
				recv_info = conf.csock1.recv(4096)
				recv_info = pickle.loads(recv_info)


		elif(conf.partyNum == 2):
			if(send_partyNum == 0):
				conf.client2.send(pickle.dumps(send_info))
				recv_info = conf.client2.recv(4096)
				recv_info = pickle.loads(recv_info)

			if(send_partyNum == 1):
				recv_info = conf.client1.recv(4096)
				recv_info = pickle.loads(recv_info)
				conf.client1.send(pickle.dumps(send_info))

		else:
			if(send_partyNum == 1):
				recv_info = conf.csock1.recv(4096)
				recv_info = pickle.loads(recv_info)
				conf.csock1.send(pickle.dumps(send_info))

			if(send_partyNum == 2):
				recv_info = conf.csock2.recv(4096)
				recv_info = pickle.loads(recv_info)
				conf.csock2.send(pickle.dumps(send_info))

		return recv_info

	def send_val(send_info,send_partyNum):
		if(conf.partyNum == 1):
			if(send_partyNum == 0):
				conf.client1.send(pickle.dumps(send_info))

			if(send_partyNum == 2):
				conf.csock1.send(pickle.dumps(send_info))

		elif(conf.partyNum == 2):
			if(send_partyNum == 0):
				conf.client2.send(pickle.dumps(send_info))

			if(send_partyNum == 1):
				conf.client1.send(pickle.dumps(send_info))

		else:
			if(send_partyNum == 1):
				conf.csock1.send(pickle.dumps(send_info))

			if(send_partyNum == 2):
				conf.csock2.send(pickle.dumps(send_info))

	def recv_val(send_info,recv_partyNum):
		if(conf.partyNum == 1):
			if(recv_partyNum == 0):
				recv_info = conf.client1.recv(4096)
				recv_info = pickle.loads(recv_info)

			if(recv_partyNum == 2):
				recv_info = conf.csock1.recv(4096)
				recv_info = pickle.loads(recv_info)


		elif(conf.partyNum == 2):
			if(recv_partyNum == 0):
				recv_info = conf.client2.recv(4096)
				recv_info = pickle.loads(recv_info)

			if(recv_partyNum == 1):
				recv_info = conf.client1.recv(4096)
				recv_info = pickle.loads(recv_info)

		else:
			if(recv_partyNum == 1):
				recv_info = conf.csock1.recv(4096)
				recv_info = pickle.loads(recv_info)

			if(recv_partyNum == 2):
				recv_info = conf.csock2.recv(4096)
				recv_info = pickle.loads(recv_info)

		return recv_info


	def randsample_2(send_partyNum): # allow any two of the three parties to sample a random value together
		conf.max_dec = primitives.int2float(2**(conf.l-1)-1)

		my_r = primitives.float2int(random.uniform(-1*conf.max_dec,conf.max_dec)) # sample a random float value from the possible range and embed it on the ring
		adv_r = primitives.send_recv_val(my_r,send_partyNum)

		r = my_r + adv_r

		return r

	def Hash(x):
		m = hashlib.sha256()
		m = m.update(bytes(str(x)))
		m = m.digest()
		return m