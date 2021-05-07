from functionalities import functionalities as func
import numpy as np
import phe as paillier
from Config import Config as conf
import math
import sys

class offline:

	def encrypt_vector(public_key, x):
		enc_x = []
		for i in range(len(x)):
			enc_x.append(public_key.encrypt(x[i][0]))
		return np.array(enc_x)

	def decrypt_vector(private_key, x):
		dec_x = []
		for i in range(len(x)):
			dec_x.append(private_key.decrypt(x[i][0]))
		return np.array(dec_x)

	def lhe(U,V, flag=0):
		# print('Entered')
		C=[]
		pubkey,privkey = paillier.generate_paillier_keypair()
		pubkeyOther = func.reconstruct([pubkey])
		pubkeyOther=pubkeyOther[0]
		#print('others pubkey ',pubkeyOther)
		for j in range(conf.t): 
			# print('In loop')
			A = np.array(U[j:j+conf.batchsize])
			if(flag != 0):
				#A = A.transpose() - doesnt work, not needed
				A = A.reshape(conf.d,1)
				# print("A.shape: ", A.shape)

			B = np.array(V[:,j])
			B = B.reshape(V.shape[0],1)
			c_0 = np.matmul(A,B) #A0B0 for S0 and A1B1 for S1 // np.uint64()
			# print("C_0.shape: ", c_0.shape)
			encrypted_B = offline.encrypt_vector(pubkey, B) #S1 encrypts B1 for A0B1 and S0 encrypts B0 A1B0
			# print("B[1]: ", sys.getsizeof(encrypted_B[1]))
			# print("type of ")
			other_B = np.array(func.reconstruct(encrypted_B.tolist()))
			other_B = other_B.reshape(V.shape[0],1) #B is d*1 or 1*1 for Vdash
			if (flag == 0):
				c_1=0
				for i in range(V.shape[0]): 
					#will only work for batchsize = 1, change for any batchsize once this works
					c_1 = c_1 + other_B[i][0]*A[0][i] #not sure about mod64, not mentioned in paper
				c_1 = np.array(c_1)
				c_1= c_1.reshape(conf.batchsize,1)		
			else :
				c_1 = []
				for i in range(A.shape[0]):
					#will only work for batchsize = 1
					temp = other_B[0][0] * A[i][0]
					c_1.append([temp])
				c_1 = np.array(c_1)
				# print("c_1.shape: ",c_1.shape)
				c_1 = c_1.reshape(A.shape[0],1) 
			
			random_num = np.array(np.random.random(size=(c_1.shape[0],1)))
			# print(random_num)
			# random_num = func.floattoint64(random_num)
			#random_num= random_num.reshape(conf.batchsize,1)
			encrypted_random = offline.encrypt_vector(pubkeyOther,random_num)
			# print("encrypted_random: ",encrypted_random)
			encrypted_random= encrypted_random.reshape(c_1.shape[0],1)
			# print("encrypted_random: ",encrypted_random)
			#c_1 = np.matmul(c_1,encrypted_random)
			c_1 = np.add(c_1,encrypted_random)
			recv = np.array(func.reconstruct(c_1.tolist()))
			recv=recv.reshape(c_1.shape[0],1)
			recv=offline.decrypt_vector(privkey,recv)
			recv=recv.reshape(c_1.shape[0],1)
			random_num = np.multiply(-1,random_num) #since -r mod 2^l
			term = np.add(c_0,recv)
			term = np.add(term,random_num)
			term = term.reshape(term.shape[0],)
			C.append(term.tolist()) #A0B0 + A0B1 + A1BO for S0, A1B1+A0B1+A1B0 for S1
			# print("C: ",np.array(C).shape)
		
		C = np.array(C)
		# print("C: ",C)
		if flag==0:
			C = C.reshape(c_1.shape[0],conf.t)
		else:
			C = np.transpose(C)
		# print("C shape: ",C.shape)
		# print('Final term: ',C)
		return C