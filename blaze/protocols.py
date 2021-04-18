#!/usr/bin/python
import sys
from config import config as conf
from shares import angular_shares as ang
from shares import special_shares as spc
from primitives import primitives as prim
import socket
import pickle
import random
import numpy as np
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
			lambda_1 = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'s')
			print("Sampled lambda_1")
			lambda_2 = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'c')
			print("Sampled lambda_2")
			lambda_ = np.uint64(lambda_1 + lambda_2)
			print("Computing lambda...")

			lambda_de_1 = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'s') # sampling lambda_de with P1
			print("Sampled lambda_de_1")
			# Step 2
			lambda_de = d.x1*e.x1
			lambda_de_2 = lambda_de - lambda_de_1

			prim.send_val(lambda_de_2,conf.advIP_2,conf.advPORT_2)
			print("Sent lambda_de_2")

		if(conf.partyNum == 1):
			lambda_ = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'c')
			print("Sampled lambda_1")
			lambda_de = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'c')
			print("Sampled lambda_de")

		if(conf.partyNum == 2):
			lambda_ = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'s')
			print("Sampled lambda_2")
			# Step 2
			lambda_de = prim.recv_val(conf.advIP_1,conf.advPORT_1)
			print("Received lambda_de")

		# Step 3
		if(conf.PRIMARY):
			f_lf = (conf.partyNum - 1)*(d.x2)*(e.x2) - (d.x1)*(e.x2) - (e.x1)*(d.x2) + lambda_de + lambda_

			if(conf.partyNum == 1):
				sorc = 's'
			else:
				sorc = 'c'

			other_f_lf = prim.send_recv_val(f_lf,conf.advIP_2,conf.advPORT_2)

			f_lf = f_lf + other_f_lf

		if(PRIMARY):
			f.x1 = lambda_
			f.x2 = f_lf
		else:
			f.x1 = lambda_1
			f.x2 = lambda_2

		return f

	def multiplication(a,b):

		c = spc()

		################# PREPROCESSING #########################
		
		# Step 1
		if(conf.partyNum == 0):
			alpha_1 = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'s')
			print("Sampled alpha_1")
			alpha_2 = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'s')
			print("Sampled alpha_2")
			print("Computing alpha...")
			alpha = np.uint64(alpha_1 + alpha_2)

		if(conf.partyNum == 1):
			alpha = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'c')
			print("Sampled alpha_1")
			gamma = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'s')
			print("Sampled gamma")

		if(conf.partyNum == 2):
			alpha = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'c')
			print("Sampled alpha_2")
			gamma = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'c')
			print("Sampled gamma")
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
			chi = chi_1 + chi_2

		if(conf.PRIMARY):

			if(conf.partyNum==1):
				chi = f.x1

			else:
				chi = f.x2

			psi = f.x2 - (e.x3)*(f.x3) #is truncation needed here?

		# Step 5
		if(conf.PRIMARY):
			r = prim.randsample_2(conf.advIP_2,conf.advPORT_2) # P1,P2 sample random r
			psi_1 = r
			psi_2 = psi - r

			Psi = [psi,psi_1,psi_2] # to access all the psi's

		# Step 6
			gamma_xy = a.x3*(b.x1) + b.x3*(a.x1) + psi[conf.partyNum] - chi


		################# ONLINE #########################

		# Step 1

		if(conf.PRIMARY):
			my_beta_z = (conf.partyNum - 1)*(a.x2)*(b.x2) - (a.x2)*(b.x1) - (b.x2)*(a.x1) + gamma_xy + alpha
			
			if(conf.partyNum == 1):
				sorc = 's'
			else:
				sorc = 'c'

			adv_beta_z = prim.send_recv_val(my_beta_z,conf.advIP_2,conf.advPORT_2,sorc)
			beta_z = my_beta_z + adv_beta_z

		# Step 2
		if(conf.partyNum == 0):
			gamma_xy = (a.x1+a.x2)*(b.x1+b.x2)
			beta_zstar = (-1)*(a.x3)*(b.x1+b.x2) - (b.x3)*(a.x1+a.x2) + alpha + 2*(gamma_xy) + chi

			prim.send_all(prim.Hash(beta_zstar))


		# Step 3
		if(conf.PRIMARY):
			
			beta_zstar = prim.recv_val(conf.advIP_1,conf.advPORT_1)
			assert beta_zstar == prim.Hash(beta_z - (a.x2)(b.x2) + psi)

			if(conf.partyNum == 1):
				# send(beta_z + gamma) to P_0
				prim.send_val((beta_z+gamma),conf.advIP_1,conf.advPORT_1)
			else:
				# P2 send(prim.Hash(beta_z + gamma)) to P_0
				prim.send_val((prim.Hash(beta_z+gamma)),conf.advIP_1,conf.advPORT_1)

		if(conf.partyNum == 0):
			# receive() from P_1
			bg = prim.recv_val(conf.advIP_1,conf.advPORT_1)
			# receive() from P_2
			h_bg = prim.recv_val(conf.advIP_2,conf.advPORT_2)
			# assert that they're are consistent
			assert prim.Hash(bg),h_bg

		if(PRIMARY):
			c.x1 = alpha
			c.x2 = beta_z
			c.x3 = gamma
		else:
			c.x1 = alpha_1
			c.x2 = alpha_2
			c.x3 = bg