#!/usr/bin/python
import sys
from Config import Config as conf
import socket
import pickle 
import random
import numpy as np
import math
import tqdm
import os

class functionalities:

	# embed an array of float values into an array of integers in the integer ring
	def floattoint64(x):
		x = np.array(conf.converttoint64*(x), dtype = np.uint64)
		return x

	# This function can be used for two purposes:
	# 1. reverse embedding from the integer ring to float
	# 2. in our codebase, we also use this function to truncate the product of two values added in the integer ring
	def int64tofloat(x,scale=1<<conf.precision):
		y=0
		if(x > (2**(conf.l-1))-1):
			x = (2**conf.l) - x
			y = np.uint64(x)
			y = y*(-1)
		else:
			y = np.uint64(x)
			
		return float(y)/(scale)

	# The truncation function proposed in the SecureML paper.
	# In our experiments, this function didn't work
	def truncate(x,scale):
		if(conf.partyNum==0):
			x = x/scale
		else:
			x = (2**conf.l) - x
			y = np.uint64(x)
			x = (y*(-1)/scale)
		return np.uint64(x)

	def send_file(file_info,filename,sz):
		with open(filename,"w+") as f:
			f.write("".join(str(file_info)))
		filesize = os.path.getsize(filename)
		# print("filesize: ", filesize)
		SEPARATOR = "--"
		BUFFER_SIZE = 4096

		if(conf.partyNum == 0):
			# send file

			ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			ssock.bind((conf.IP, conf.PORT))
			ssock.listen()
			# ssock.settimeout(30)
			while True:
				try:
					# print('Waiting for connection at : ',conf.IP,conf.PORT)
					client, addr = ssock.accept()
					# print('Received connection ')
					break
				except:
					continue
	
			client.send(f"{filename}{SEPARATOR}{filesize}".encode())
		
			# print(f"Sending {filename}")
			with open(filename, "rb") as f:
				bytes_read = f.read(filesize)		
				client.sendall(bytes_read)

			# print("Sent! Now receiving...")
			
			# receive file

			received = client.recv(sz).decode()
			# print(received)
			fname, fsize = received.split(SEPARATOR)
			b = math.ceil(int(fsize)/BUFFER_SIZE)
			# print(b)
			# print(f"Receiving other_{filename}")
			with open(str("other_")+filename, "wb") as f:
				bytes_read = client.recv(int(fsize))
				f.write(bytes_read)
				f.flush()	
		
			# print("Received")
			client.close()
			ssock.close()

		else:
			csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# csock.settimeout(30)
			while True:
				try:
					csock.connect((conf.advIP,conf.advPORT))
					# print("Connected")
					break
				except: 
					continue
			# receive file
			received = csock.recv(sz).decode()
			# print(received)
			fname, fsize = received.split(SEPARATOR)
			b = math.ceil(int(fsize)/BUFFER_SIZE)
			# print(b)
			# print(f"Receiving other_{filename}")
			with open(str("other_")+filename, "wb") as f:
				bytes_read = csock.recv(int(fsize))
				f.write(bytes_read)
				f.flush()						
			# print("Received")
					
			# send file

			csock.send(f"{filename}{SEPARATOR}{filesize}".encode())
			# print(f"Sending {filename}")
			with open(filename, "rb") as f:
				bytes_read = f.read(filesize)			
				csock.sendall(bytes_read)
			# print("Sent!")
			csock.close()

		# print("Returning...")
		return

	def send_val(send_info):
		# print("Size of send info: ",sys.getsizeof(send_info))
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
			# client, addr = ssock.accept()
			# print("Size of send val: ",sys.getsizeof(send_info))
			recv_info = client.recv(4096)
			recv_info = pickle.loads(recv_info)
			client.send(pickle.dumps(send_info))
			client.close()
			ssock.close()
		else: 
			csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			while True:
				try:
					csock.connect((conf.advIP,conf.advPORT))
					# print("Connected")
					break
				except: 
					continue
			# csock.connect((conf.advIP,conf.advPORT))
			# csock.setblocking(True)		
			# print("Size of send val: ",sys.getsizeof(send_info))
			csock.send(pickle.dumps(send_info))
			recv_info = pickle.loads(csock.recv(4096))
			# csock.shutdown(socket.SHUT_RDWR)
			csock.close()
		return recv_info

	def addshares(a, b, mask):
		sendlist = []
		sum1 = (a + b + mask) 
		sendlist.append(sum1)
		sum2 = send_val(sendlist)
		
		return sum1+sum2[0]

	def reconstruct(c):
		C = functionalities.send_val(c)
		return C

	def multiplyshares(a,b,u,v,z):
		sendlist = []
		e = a - u
		f = b - v
		sendlist.append(e)
		sendlist.append(f)
		recv_info = send_val(sendlist)
		E = e + recv_info[0]
		F = f + recv_info[1]
		c = (-1 * conf.partyNum * E * F) + (a * F) + (E * b) + z
		sendlist=[]
		sendlist.append(c)
		C = reconstruct(sendlist)
		return C[0]+c

	def matrixadd(A,B,mask):
		sum1 = np.add(np.array(A),np.array(B))
		sum2 = send_val(sum1.tolist())		

		return (np.add(np.array(sum2)),sum1).tolist()

	def matrixmul(A,B,U,V,Z):
		A = np.array(A)
		B = np.array(B)
		U = np.array(U)
		V = np.array(V)
		
		E = np.subtract(A,U)
		F = np.subtract(B,V)

		sendlist = []
		sendlist.append(E.tolist())
		sendlist.append(F.tolist())
		recv_info = send_val(sendlist)

		E = E + recv_info[0]
		F = F + recv_info[1]

		c = np.add(-1 * conf.partyNum * (np.multiply(E,F)),np.multiply(A*F) + np.multiply(E*B))
		C = reconstruct(c.tolist())

		C = (np.add(np.array(C),c).tolist())
		
		return C

	def addvectors(A,B):
		m,n = A.shape
		C = np.array([[0]*n]*m)
		for i in range(m):
			for j in range(n):
				print(i,j)
				C[i][j] = (A[i][j] + B[i][j])%(2**conf.l)
				print(C[i][j])
		return C

	def matrixmul_reg(A,B,E,F,V,Z):
		# A - data pt
		# B - weights
		# E = datapoint - data mask U
		# V - mask of weights for this batch
		# F = weights - weights mask V

		mul1 = np.matmul(E,F)
		for i in range(len(mul1)):
			mul1[i][0] = np.uint64(functionalities.int64tofloat(mul1[i][0]))
		mul2 = np.matmul(A,F)
		for i in range(len(mul2)):
			mul2[i][0] = np.uint64(functionalities.int64tofloat(mul2[i][0]))
		mul3 = np.matmul(E,B)
		for i in range(len(mul3)):
			mul3[i][0] = np.uint64(functionalities.int64tofloat(mul3[i][0]))
		mul0 = np.multiply(functionalities.floattoint64(-1 * conf.partyNum), mul1)
		for i in range(len(mul0)):
			mul0[i][0] = np.uint64(functionalities.int64tofloat(mul0[i][0]))

		Yhat1 = np.add(mul0,mul2)
		Yhat2 = np.add(mul3,Z)
		Yhat = np.add(Yhat1,Yhat2)

		return Yhat