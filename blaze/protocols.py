#!/usr/bin/python
import sys
from config import config as conf
from shares import angular_shares as ang
from shares import special_shares as spc
import socket
import pickle 
import random
import numpy as np
import math
import os

class protocols:

	def mulZK(d,e):
		return f

	def multiplication(a,b):

		################# PREPROCESSING #########################
		
		# Step 1
		if(conf.partyNum == 0):
			alpha_1 = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'s')
			alpha_2 = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'s')
			alpha = alpha_1 + alpha_2

		if(conf.partyNum == 1):
			alpha = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'c')
			gamma = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'s')

		if(conf.partyNum == 2):
			alpha = prim.randsample_2(conf.advIP_1,conf.advPORT_1,'c')
			gamma = prim.randsample_2(conf.advIP_2,conf.advPORT_2,'c')

		# Step 2
		d = ang()
		e = ang()

		if(conf.partyNum == 0):
			d.x1 = a.x1
			d.x2 = a.x2
			e.x1 = b.x1
			e.x2 = b.x2

		if(conf.partyNum == 1 or conf.partyNum == 2):
			d.x1 = a.x1
			d.x2 = a.x3
			e.x1 = e.x1
			e.x2 = e.x3

		# Step 3
		f = mulZK(d,e)

		# Step 4
		if(conf.partyNum == 0):
			chi_1 = f.x1
			chi_2 = f.x2
			chi = chi_1 + chi_2

		if(conf.partyNum == 1 or conf.partyNum == 2):

			if(conf.partyNum==1):
				chi = f.x1

			else:
				chi = f.x2

			psi = f.x2 - (e.x3)*(f.x3) #is truncation needed here?

		# Step 5
		if(conf.partyNum == 1 or conf.partyNum == 2):
			r = prim.randsample_2(conf.advIP_2,conf.advPORT_2) # P1,P2 sample random r
			psi_1 = r
			psi_2 = psi - r

			Psi = [psi,psi_1,psi_2] # to access all the psi's

		# Step 6
			gamma_xy = a.x3*(b.x1) + b.x3*(a.x1) + psi[conf.partyNum] - chi


		################# ONLINE #########################

		# Step 1

		if(conf.partyNum == 1 or conf.partyNum == 2):
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
		if(conf.partyNum == 1 or conf.partyNum == 2):
			
			beta_zstar = prim.recv_val(conf.advIP_1,conf.advPORT_1)
			assert(beta_zstar == prim.Hash(beta_z - (a.x2)(b.x2) + psi))

			if(conf.partyNum == 1):
				# send(beta_z + gamma) to P_0
				prim.send_val((beta_z+gamma),conf.advIP_1,conf.advPORT_1)
			else:
				# P2 send(prim.Hash(beta_z + gamma)) to P_0
				prim.send_val((prim.Hash(beta_z+gamma)),conf.advIP_1,conf.advPORT_1)

		if(conf.partyNum == 0):
			# receive() from P_1
			bg = recv_val(conf.advIP_1,conf.advPORT_1)
			# receive() from P_2
			h_bg = recv_val(conf.advIP_2,conf.advPORT_2)
			# assert that they're are consistent
			assert(prim.Hash(bg),h_bg)