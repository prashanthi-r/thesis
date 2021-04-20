#!/usr/bin/python
import sys
from config import config as conf
from shares import angular_share as ang
from shares import special_share as spc
from primitives import primitives as prim
import socket
import pickle
import random
import numpy as np
import time
# import math
# import os

class protocols:

	def mulZK(d,e): 

	# mulZK is from: D. Boneh, E. Boyle, H. Corrigan-Gibbs, N. Gilboa, and Y. Ishai,
	# “Zero-knowledge proofs on secret-shared data via fully linear pcps,”
	# in CRYPTO, 2019, pp. 67–97.
	
	# The implementation of verification by zero knowledge proofs is not done.
	# This function will be used as a black box. We will be assuming that 
	# this protocol is honestly executed by each server.

		f = ang() # creating a data class object for an angular share

		# Step 1
		if(conf.partyNum == 0):
			lambda_1 = prim.randsample_2(1)
			print("0: Sampled lambda_1")
			lambda_2 = prim.randsample_2(2)
			print("0: Sampled lambda_2")
			lambda_ = np.uint64(np.add(lambda_1,lambda_2))
			print("0: Computing lambda...")

			lambda_de_1 = prim.randsample_2(1) # sampling lambda_de with P1
			print("0: Sampled lambda_de_1")
			# Step 2
			lambda_de = np.uint64(np.multiply(d.x1,e.x1))
			lambda_de_2 = np.uint64(np.subtract(lambda_de,lambda_de_1))

			prim.send_val(lambda_de_2,2)
			print("0: Sent lambda_de_2")

		if(conf.partyNum == 1):
			lambda_ = prim.randsample_2(0)
			print("1: Sampled lambda_1")
			lambda_de = prim.randsample_2(0)
			print("1: Sampled lambda_de")

		if(conf.partyNum == 2):
			lambda_ = prim.randsample_2(0)
			print("2: Sampled lambda_2")
			# lambda_de_1 = prim.randsample_2(1)
			# print("2: Sampled lambda_de")
			# Step 2
			lambda_de = prim.recv_val(0) # this value would be lambda_de_2
			print("2: Received lambda_de")


		# Step 3
		if(conf.PRIMARY):
			f_lf = np.uint64(np.add(np.subtract(np.subtract(np.multiply(conf.partyNum - 1,np.multiply(d.x2,e.x2)),np.multiply(d.x1,e.x2)),np.multiply(e.x1,d.x2)),np.add(lambda_de,lambda_)))

			other_f_lf = prim.send_recv_val(f_lf,conf.adv_party)

			f_lf = np.uint64(np.add(f_lf,other_f_lf))

			# setting the share

			f.x1 = lambda_
			f.x2 = f_lf

		else:
			# setting the share
			f.x1 = lambda_1
			f.x2 = lambda_2

		return f

	def multiplication(a,b):

		c = spc()

		################# PREPROCESSING #########################
		
		# Step 1
		if(conf.partyNum == 0):
			alpha_1 = prim.randsample_2(1)
			print("Sampled alpha_1")
			alpha_2 = prim.randsample_2(2)
			print("Sampled alpha_2")
			print("Computing alpha...")
			alpha = np.uint64((np.add(alpha_1,alpha_2)))

		if(conf.partyNum == 1):
			alpha = prim.randsample_2(0)
			print("Sampled alpha_1")
			gamma = prim.randsample_2(2)
			print("Sampled gamma")

		if(conf.partyNum == 2):
			alpha = prim.randsample_2(0)
			print("Sampled alpha_2")
			gamma = prim.randsample_2(1)
			print("Sampled gamma: ", gamma)

		
		# Step 2
		d = ang()
		e = ang()

		if(conf.partyNum == 0):
			d.x1 = a.x1
			d.x2 = a.x2
			e.x1 = b.x1
			e.x2 = b.x2

		if(conf.PRIMARY):
			d.x1 = a.x1
			d.x2 = a.x3
			e.x1 = b.x1
			e.x2 = b.x3

		# Step 3
		f = protocols.mulZK(d,e)

		# Step 4
		if(conf.partyNum == 0):
			chi_1 = f.x1
			chi_2 = f.x2
			chi = np.uint64(np.add(chi_1,chi_2))

		if(conf.PRIMARY):
			chi = f.x1

			psi = np.uint64(np.subtract(f.x2,np.multiply((a.x3),(b.x3)))) # is truncation needed here?

		# Step 5
		if(conf.PRIMARY):
			r = prim.randsample_2(conf.adv_party) # P1,P2 sample random r
			psi_1 = r
			psi_2 = np.uint64(np.subtract(psi,r))

			Psi = [psi,psi_1,psi_2] # to access all the psi's

		# Step 6
			gamma_xy = (np.add(np.add(np.multiply(a.x3,b.x1),np.multiply(b.x3,a.x1)),np.subtract(Psi[conf.partyNum],chi)))
			print(str(conf.partyNum)+" gamma_xy",gamma_xy)

		##################### ONLINE #########################

		# Step 1

		if(conf.PRIMARY):
			my_beta_z = np.uint64(np.add(np.subtract(np.subtract(np.multiply(conf.partyNum - 1,np.multiply((a.x2),(b.x2))),np.multiply((a.x2),(b.x1))),np.multiply((b.x2),(a.x1))),np.add(gamma_xy,alpha)))

			adv_beta_z = prim.send_recv_val(my_beta_z,conf.adv_party)
			beta_z = np.uint64(np.add(my_beta_z,adv_beta_z))
			print(str(conf.partyNum)+" beta_z",beta_z)
			print("psi: ",Psi[0])
			print("Bxby: ",np.multiply((a.x2),(b.x2)))

		# Step 2
		if(conf.partyNum == 0):
			gamma_xy = np.multiply(np.add(a.x1,a.x2),np.add(b.x1,b.x2)) # gamma_xy = alpha_x X alpha_y
			print("0 gamma_xy",gamma_xy)
			beta_zstar = np.uint64(np.add(np.subtract(np.multiply(-1,np.multiply((a.x3),np.add(b.x1,b.x2))),np.multiply(b.x3,np.add(a.x1,a.x2))),np.add(np.add(alpha,np.multiply(2,gamma_xy)),chi)))
			print('0: beta_zstar: ',beta_zstar)
			print('0: Hash(beta_zstar): ',prim.Hash(beta_zstar))
			prim.send_val(prim.Hash(beta_zstar),1)
			prim.send_val(prim.Hash(beta_zstar),2)


		# Step 3
		if(conf.PRIMARY):
			
			beta_zstar = prim.recv_val(0)
			print('beta_zstar: ',beta_zstar)
			print("Hash: ",prim.Hash(np.uint64(np.subtract(beta_z,np.add(np.multiply((a.x2),(b.x2)),psi)))))
			print('beta_zstar computed: ',np.uint64(np.subtract(beta_z,np.add(np.multiply((a.x2),(b.x2)),psi))))
			assert beta_zstar - prim.Hash(np.uint64(np.subtract(beta_z,np.add(np.multiply((a.x2),(b.x2)),psi))))

			if(conf.partyNum == 1):
				# send(beta_z + gamma) to P_0
				prim.send_val(np.uint64(np.add(beta_z,gamma)),0)
			else:
				# P2 send(prim.Hash(beta_z + gamma)) to P_0
				prim.send_val(prim.Hash(np.uint64(np.add(beta_z,gamma))),0)

		if(conf.partyNum == 0):
			# receive() from P_1
			bg = prim.recv_val(1)
			# receive() from P_2
			h_bg = prim.recv_val(2)
			# assert that they're are consistent
			assert prim.Hash(bg),h_bg

		if(conf.PRIMARY):
			c.x1 = alpha
			c.x2 = beta_z
			c.x3 = gamma
		else:
			c.x1 = alpha_1
			c.x2 = alpha_2
			c.x3 = bg

		return c