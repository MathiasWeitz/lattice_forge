# -*- coding: cp1252 -*-
from math import *
import logging
fformat = "%6.7f"


class matrix:
	def __init__(self):
		self.field = [[0]]

	def set(self,y,x,value):
		while len(self.field) <= y:
			self.field.append([0])
		while len(self.field[y]) <= x:
			self.field[y].append(0)
		self.field[y][x] = value

	def get(self,y,x):
		erg = 0
		if y < len(self.field):
			if x < len(self.field[y]):
				erg = self.field[y][x]
		return erg

	def dimX(self):
		erg = 0
		for i in range(len(self.field)):
			if erg < len(self.field[i]):
				erg = len(self.field[i])
		return erg

	def copy(self):
		erg = matrix()
		for i in range(len(self.field)):
			for j in range(len(self.field[i])):
				erg.set(i,j,self.field[i][j])
		return erg

	def dimY(self):
		return len(self.field)

	def t_copy(self):
		# transponierte Matrix
		erg = matrix()
		for i in range(len(self.field)):
			for j in range(len(self.field[i])):
				erg.set(j,i,self.field[i][j])
		return erg

	def write(self):
		for v1 in self.field:
			e = ''
			for v2 in v1:
				e += "%7.3f" % v2
			print (e)
			
	def writeWMaxima(self, name='d'):
		follow1 = False
		erg = name + ':matrix('
		for v1 in self.field:
			if follow1:
				erg += ','
			follow1 = True
			erg += '['
			follow2 = False
			dimX = self.dimX()
			for v2i in range(dimX):
				if follow2:
					erg += ','
				follow2 = True
				v2 = 0.0
				if v2i < len(v1):
					v2 = v1[v2i]
				if abs(v2) < 1e-12:
					erg += '0.0'
				else:
					erg += str(v2)
			erg += ']'
		return erg + ');'

	def mul(self,y,a):
		# multipliziert Zeile y mit a
		if y < len(self.field):
			for i in range(len(self.field[y])):
				self.field[y][i] *= a

	def sub(self,y1,y2):
		# zieht von Zeile y1 die Zeile y2 ab
		if y2 < len(self.field):
			maxl = len(self.field[y2])
			if y1 < len(self.field):
				maxl = max(maxl,len(self.field[y2]))
			for i in range(maxl):
				self.set(y1,i, self.get(y1,i) - self.get(y2,i))

	def change(self,y1,y2):
		# tauscht Zeile y1 mit Zeile y2
		for i in range(self.dimX()):
			h = self.get(y1, i)
			self.set(y1, i, self.get(y2, i))
			self.set(y2, i, h)

	def mul_matrix(self, m):
		# multipliziert zwei Matrizen miteinander
		erg = matrix()
		if self.dimX() == m.dimY():
			for y in range(self.dimY()):
				for x in range(m.dimX()):
					s = 0
					for k in range(self.dimX()):
						s += self.get(y,k) * m.get(k,x)
					erg.set(y,x,s)
		return erg

	def mul_vektor(self, v):
		# multipliziert eine Matriz mit einem Array (= Vektor)
		erg = []
		#rprint ("mul_vektor", self.dimX(), len(v))
		if self.dimX() == len(v):
			for y in range(self.dimY()):
				s = 0
				for k in range(self.dimX()):
					s += self.get(y,k) * v[k]
				erg.append(s)
		return erg

	def getZeros(self):
		# unbestimmbare Spalten ermitteln
		erg = []
		if self.dimX() == self.dimY():
			for y in range(self.dimY()):
				isZero = True
				for x in range(self.dimY()):
					#print ("zero test", self.get(y,x), self.get(x,y))
					isZero &= abs(self.get(y,x)) < 1e-4
					isZero &= abs(self.get(x,y)) < 1e-4
				if isZero:
					erg.append(y)
		return erg
		
	def appendCol(self, col, neg = False):
		# Spalte anhaengen
		dimX = self.dimX()
		for i in range(len(col)):
			self.set(i,dimX,col[i]);
		return self

	def cholesky(self, e):
		logging.info(self.writeWMaxima('chol_s'))
		l = matrix()
		for k in range(len(self.field)):
			pivot = self.get(k,k)
			if 0 < pivot: 
				l.set(k,k,sqrt(pivot))
				for i in range(k+1,len(self.field)):
					l1 = self.get(i,k)/l.get(k,k)
					l.set(i,k,l1)
					for j in range(k+1,i+1):
						self.set(i,j,self.get(i,j) - l.get(i,k) * l.get(j,k))
		logging.info(l.writeWMaxima('chol_l'))
		c = []
		for i in range(len(e)):
			s = e[i]
			for j in range(i):
				s -= l.get(i,j) * c[j]
			c.append(s / l.get(i,i))
		logging.info(c)
		x = [0] * len(c)
		for i in range(len(e)-1,-1,-1):
			s = c[i]
			for k in range(i+1, len(e)):
				s += l.get(k,i) * x[k]
			x[i] = -s / l.get(i,i)
		logging.info('x: ' + str(x))
		return x

	def gauss(self, e):
		# print ("********************** lineare Gleichung")
		# lineare Gleichung nach Gauss
		while len(e) < len(self.field):
			e.append(0)
		# forward-Schritt
		i = 0
		lenField = len(self.field)
		while i < lenField-1:
			#print ("forward",i)
			#self.write()
			#print (e)
			logging.info (self.writeWMaxima('zf' + str(i)))
			pivotE = self.get(i,i)
			#print "Pivot", pivotE
			if 1e-5 < abs(pivotE):
				# alles wie es sein soll
				for j in range(i+1, len(self.field)):
					#print "gauss, forward", i,j
					pivotJ = self.get(j,i)
					#print "Pivot2", pivotJ
					if 1e-5 < abs(pivotJ):
						faktor = pivotE/pivotJ
						self.mul(j, faktor)
						e[j] *= faktor
						e[j] -= e[i]
						self.sub(j,i)
				i += 1
			else:
				erg = 0
				# suche eine Zeile zum tauschen
				for j in range(i+1, len(self.field)):
					if i < len(self.field[j]) and 1e-5 < abs(self.field[j][i]):
						erg = j
				if 0 < erg:
					self.change(i,erg)
					h = e[i]
					e[i] = e[erg]
					e[erg] = h
				else:
					# Ausnahme, 0-Zeile
					i += 1
		# test real rank
		rank = len(self.field)-1
		test_ranking = True
		while 0 <= rank and test_ranking:
			for i in range(len(self.field[rank])):
				if 1e-5 < abs(self.field[rank][i]):
					test_ranking = False
			if test_ranking:
				rank -= 1
		logging.info ('rank: ' + str(rank))
		if 0 < rank and rank < len(self.field)-1:
			subMatrixStart = len(self.field)-rank-1
			subMatrix = matrix()
			for i1 in range(rank+1):
				for i2 in range(rank+1):
					subMatrix.set(i1, i2, self.get(i1, i2+subMatrixStart))
			logging.info (subMatrix.writeWMaxima('subm'))
		# backward-Schritt
		lin = False
		for i in range(len(self.field)-1,0,-1):
			#print ("backward",i)
			#self.write()
			#print (e)
			logging.info (self.writeWMaxima('zb' + str(i)))
			pivotE = self.get(i,i)
			if 1e-5 < abs(pivotE):
				for j in range(0,i):
					#print ("gauss, 2backward", i,j)
					pivotJ = self.get(j,i)
					if 1e-5 < abs(pivotJ):
						faktor = pivotE/pivotJ
						self.mul(j, faktor)
						e[j] *= faktor
						e[j] -= e[i]
						self.sub(j,i)

				pivotK = self.get(i,i)
				if 1e-7 < abs(pivotK):
					e[i] /= pivotK
				else:
					e[i] = 0
					#lin = True
		pivotK = self.get(0,0)
		if 1e-7 < abs(pivotK):
			e[0] /= pivotK
		#else:
		#   lin = True
		#print ("e", e)
		#if lin:
		#   e = None
		return e

class point:
	point = {}
	def __init__(self, point):
		self.point = point
		
	def coor(self):
		return self.point

class trajectory:
	point = {}
	offset = {1: 0.0, 2:0.0, 3:0.0}
	w = {1: 0.0, 2:0.0, 3:0.0, 4:0.0, 5:0.0, 6:0.0, 7:1.0}
	trajectoryPoint = None
	verbose = 0
	h = 0.0
	diff = (0.0, 0.0, 0.0)
	isCalculated = False

	def __init__(self, point):
		self.point = point

	def setTrajectoryPoint(self, point):
		self.trajectoryPoint = point
		
	def getPoint(self):
		self.calculate()
		return self.point
		
	def setParameter(self, w):
		self.w = w
		return self
		
	def setOffset(self, offset):
		self.offset = offset

	def getH(self):
		self.calculate()
		return self.h
	
	def getD(self):
		self.calculate()
		return self.diff

	def log(self, text=''):
		logging.info (text)
		return self

	def calculate(self):
		if not self.isCalculated:
			p = self.trajectoryPoint.coor()
			p[1] -= self.offset[1]
			p[2] -= self.offset[2]
			p[3] -= self.offset[3]
			
			v = self.point
			v[1] -= self.offset[1]
			v[2] -= self.offset[2]
			v[3] -= self.offset[3]
			#print (p)
			w = self.w
			vp = {}
			vr = {}
			# Rotationmatrix multiplied with targetvector (this is vector one we do refer to)
			# vr is used for the derivative to the scalr
			vr[1] = v[3]*(sin(w[1])*sin(w[3])-cos(w[1])*sin(w[2])*cos(w[3]))+v[2]*(-cos(w[1])*sin(w[3])-sin(w[1])*sin(w[2])*cos(w[3]))+v[1]*cos(w[2])*cos(w[3])
			vr[2] = v[2]*(cos(w[1])*cos(w[3])-sin(w[1])*sin(w[2])*sin(w[3]))+v[3]*(-cos(w[1])*sin(w[2])*sin(w[3])-sin(w[1])*cos(w[3]))+v[1]*cos(w[2])*sin(w[3])
			vr[3] = v[1]*sin(w[2])+v[2]*sin(w[1])*cos(w[2])+v[3]*cos(w[1])*cos(w[2])

			# after rotation multiply with scale and add translation
			vp[1] = w[4] + vr[1]*w[7]
			vp[2] = w[5] + vr[2]*w[7]
			vp[3] = w[6] + vr[3]*w[7]

			# Derivative of the Rotationmatrix
			Mp_diffwx = {1: w[7] * (v[2]*(sin(w[1])*sin(w[3])-cos(w[1])*sin(w[2])*cos(w[3]))+v[3]*(cos(w[1])*sin(w[3])+sin(w[1])*sin(w[2])*cos(w[3]))), \
						2: w[7] * (v[3]*(sin(w[1])*sin(w[2])*sin(w[3])-cos(w[1])*cos(w[3]))+v[2]*(-cos(w[1])*sin(w[2])*sin(w[3])-sin(w[1])*cos(w[3]))), \
						3: w[7] * (v[2]*cos(w[1])*cos(w[2])-v[3]*sin(w[1])*cos(w[2]))}

			Mp_diffwy = {1: w[7] * (-v[1]*sin(w[2])*cos(w[3])-v[2]*sin(w[1])*cos(w[2])*cos(w[3])-v[3]*cos(w[1])*cos(w[2])*cos(w[3])), \
						2: w[7] * (-v[1]*sin(w[2])*sin(w[3])-v[2]*sin(w[1])*cos(w[2])*sin(w[3])-v[3]*cos(w[1])*cos(w[2])*sin(w[3])), \
						3: w[7] * (-v[2]*sin(w[1])*sin(w[2])-v[3]*cos(w[1])*sin(w[2])+v[1]*cos(w[2]))}

			Mp_diffwz = {1: w[7] * (v[2]*(sin(w[1])*sin(w[2])*sin(w[3])-cos(w[1])*cos(w[3]))+v[3]*(cos(w[1])*sin(w[2])*sin(w[3])+sin(w[1])*cos(w[3]))-v[1]*cos(w[2])*sin(w[3])), \
						2: w[7] * (v[3]*(sin(w[1])*sin(w[3])-cos(w[1])*sin(w[2])*cos(w[3]))+v[2]*(-cos(w[1])*sin(w[3])-sin(w[1])*sin(w[2])*cos(w[3]))+v[1]*cos(w[2])*cos(w[3])), \
						3: 0}

			Mp_difftx = {1: 1.0, 2: 0.0, 3: 0.0}
			Mp_diffty = {1: 0.0, 2: 1.0, 3: 0.0}
			Mp_difftz = {1: 0.0, 2: 0.0, 3: 1.0}

			Mp_diffs = vr
 
			# difference to the trajecting point (this is vector two we do refer to)
			dist = {1:vp[1] - p[1],2:vp[2] - p[2],3:vp[3] - p[3]}
			# the out-commented lines are for the version, which used distance-estimating by pythagoras - this didn't work out that well
			#distx2,disty2,distz2 = dist[1]*dist[1], dist[2]*dist[2], dist[3]*dist[3]
			#target = sqrt(distx2 + disty2 + distz2)

			# derivative of trajecting point
			#dist_diffwx = (dist[1] * Mp_diffwx[1] + dist[2] * Mp_diffwx[2] + dist[3] * Mp_diffwx[3]) / target
			#dist_diffwy = (dist[1] * Mp_diffwy[1] + dist[2] * Mp_diffwy[2] + dist[3] * Mp_diffwy[3]) / target
			#dist_diffwz = (dist[1] * Mp_diffwz[1] + dist[2] * Mp_diffwz[2] + dist[3] * Mp_diffwz[3]) / target
			#dist_difftx = (dist[1] * Mp_difftx[1] + dist[2] * Mp_difftx[2] + dist[3] * Mp_difftx[3]) / target
			#dist_diffty = (dist[1] * Mp_diffty[1] + dist[2] * Mp_diffty[2] + dist[3] * Mp_diffty[3]) / target
			#dist_difftz = (dist[1] * Mp_difftz[1] + dist[2] * Mp_difftz[2] + dist[3] * Mp_difftz[3]) / target
			#dist_diffs  = (dist[1] * Mp_diffs[1] + dist[2] * Mp_diffs[2] + dist[3] * Mp_diffs[3]) / target

			#self.h = target
			#self.diff = {1:dist_diffwx, 2:dist_diffwy, 3:dist_diffwz, 4:dist_difftx, 5:dist_diffty, 6:dist_difftz, 7:dist_diffs }
			self.h = [dist[1], dist[2], dist[3]]
			self.diff = [
				{1:Mp_diffwx[1], 2:Mp_diffwy[1], 3:Mp_diffwz[1], 4:Mp_difftx[1], 5:Mp_diffty[1], 6:Mp_difftz[1], 7:Mp_diffs[1] },
				{1:Mp_diffwx[2], 2:Mp_diffwy[2], 3:Mp_diffwz[2], 4:Mp_difftx[2], 5:Mp_diffty[2], 6:Mp_difftz[2], 7:Mp_diffs[2] },
				{1:Mp_diffwx[3], 2:Mp_diffwy[3], 3:Mp_diffwz[3], 4:Mp_difftx[3], 5:Mp_diffty[3], 6:Mp_difftz[3], 7:Mp_diffs[3] },
			]
			logging.info('vp ' + str(vp))
			self.point = point({1: self.offset[1] + vp[1], 2: self.offset[2] + vp[2], 3: self.offset[3] + vp[3]})
			self.isCalculated = True
			#
				
			if 1 == self.verbose:
				# nomenklatura for wxmaxima
				self.log ("load(vect);")
				self.log ("define (Ax(w), matrix([1,0,0],[0,cos(w[1]),-sin(w[1])],[0,sin(w[1]),cos(w[1])]));")
				self.log ("define (Ay(w), matrix([cos(w[2]),0,-sin(w[2])],[0,1,0],[sin(w[2]),0,cos(w[2])]));")
				self.log ("define (Az(w), matrix([cos(w[3]),-sin(w[3]),0],[sin(w[3]),cos(w[3]),0],[0,0,1]));")
				self.log ("define (M(w), Az(w).Ay(w).Ax(w));")
				self.log ("define(V(v),matrix([v[1],v[2],v[3]]));")
				self.log ("define(Mp(w,v), M(w).[v[1]*w[7],v[2]*w[7],v[3]*w[7]] + [[w[4]],[w[5]],[w[6]]]);")
				
				self.log ("define(Mp_diffwx(w,v), diff(Mp(w,v),w[1]));")
				self.log ("define(Mp_diffwy(w,v), diff(Mp(w,v),w[2]));")
				self.log ("define(Mp_diffwz(w,v), diff(Mp(w,v),w[3]));")
				self.log ("define(Mp_difftx(w,v), diff(Mp(w,v),w[4]));")
				self.log ("define(Mp_diffty(w,v), diff(Mp(w,v),w[5]));")
				self.log ("define(Mp_difftz(w,v), diff(Mp(w,v),w[6]));")
				self.log ("define(Mp_diffs(w,v), diff(Mp(w,v),w[7]));")
				
				#self.log ("P:[" + str(p[1]) + "," + str(p[2]) + "," + str(p[3]) + "];")
				#self.log ("define(target(w,v), sqrt((P-Mp(w,v)).(P-Mp(w,v))));")
				#self.log ("define(target_diffwx(w,v), diff(target(w,v),w[1]));")
				#self.log ("define(target_diffwy(w,v), diff(target(w,v),w[2]));")
				#self.log ("define(target_diffwz(w,v), diff(target(w,v),w[3]));")
				#self.log ("define(target_difftx(w,v), diff(target(w,v),w[4]));")
				#self.log ("define(target_diffty(w,v), diff(target(w,v),w[5]));")
				#self.log ("define(target_difftz(w,v), diff(target(w,v),w[6]));")
				#self.log ("define(target_diffs(w,v), diff(target(w,v),w[7]));")
				
				self.log()
				arg = '[' + str(w[1]) + ',' + str(w[2]) + ',' + str(w[3]) + ',' +  str(w[4]) + ',' +  str(w[5]) + ',' +  str(w[6]) + ',' +  str(w[7]) + '],[' + str(v[1]) + ',' +  str(v[2]) + ',' + str(v[3]) + ']'
				self.log("Mp(" + arg + ") = " + str(vp))
				self.log("Mp_diffwx(" + arg + ") = " + str(Mp_diffwx))
				self.log("Mp_diffwy(" + arg + ") = " + str(Mp_diffwy))
				self.log("Mp_diffwz(" + arg + ") = " + str(Mp_diffwz))
				self.log("Mp_difftx(" + arg + ") = " + str(Mp_difftx))
				self.log("Mp_diffty(" + arg + ") = " + str(Mp_diffty))
				self.log("Mp_difftz(" + arg + ") = " + str(Mp_difftz))
				self.log("Mp_diffs(" + arg + ") = " + str(Mp_diffs))
				#self.log("target(" + arg + ") = " + str(target))
				
				#self.log("target_diffwx(" + arg + ") = " + str(dist_diffwx))
				#self.log("target_diffwy(" + arg + ") = " + str(dist_diffwy))
				#self.log("target_diffwz(" + arg + ") = " + str(dist_diffwz))
				#self.log("target_difftx(" + arg + ") = " + str(dist_difftx))
				#self.log("target_diffty(" + arg + ") = " + str(dist_diffty))
				#self.log("target_difftz(" + arg + ") = " + str(dist_difftz))
				#self.log("target_diffs(" + arg + ") = " + str(dist_diffs))
	
	
logging.basicConfig(filename='c:\\tmp\\python.log', format='%(message)s', level=logging.INFO)
	
pointsCo1 = [
{0: [ 0.5,  0.5, 0], 1: [ 1.0,  1.0, 1.0]}, 
{0: [ 0.5, -0.5, 0], 1: [ 1.0, -1.0, 1.0]}, 
{0: [-0.5,  0.5, 0], 1: [-1.0,  1.0, 1.0]}, 
{0: [-0.5, -0.5, 0], 1: [-1.0, -1.0, 1.0]}
]	

pointsCo2 = [
{0: [ 0.5,  0.5, 0], 1: [ 1.0,  1.0, 2.0]}, 
{0: [ 0.5, -0.5, 0], 1: [ 1.0, -1.0, 2.0]}, 
{0: [-0.5,  0.5, 0], 1: [-1.0,  1.0, 1.0]}, 
{0: [-0.5, -0.5, 0], 1: [-1.0, -1.0, 1.0]}
]	

pointsCo3 = [
{0: [-1.5, -0.5, 0], 1: [-0.5, -0.5, -0.5]}, 
{0: [-0.5, -0.5, 0], 1: [ 0.5, -0.5, -0.5]}, 
{0: [-1.5, -1.5, 0], 1: [-0.5,  0.5, -0.5]}, 
{0: [-0.5, -1.5, 0], 1: [ 0.5,  0.5, -0.5]}
]	

pointsCo = pointsCo3

w = {1: 0.0 , 2: 0.0 , 3: 0.0 , 4: 0.0 , 5: 0.0 , 6: 0.0 , 7: 1.0 }
rep = 12
while 0 < rep:
	rep -= 1
	m = matrix()
	e = []
	i = 0
	for pointCo in pointsCo:
		p = {1:pointCo[0][0], 2:pointCo[0][1], 3:pointCo[0][2]}
		t = point({1:pointCo[1][0], 2:pointCo[1][1], 3:pointCo[1][2]})
		tObj = trajectory(p)
		tObj.setTrajectoryPoint(t)
		tObj.setOffset({1:0.0, 2:0.0, 3:0.0})
		tObj.setParameter(w)
		h = tObj.getH()
		d = tObj.getD()
		pp = tObj.getPoint()
		pointCo[2] = pp.coor()
		for j in range(len(h)):
			m.set(i,0,d[j][1])
			m.set(i,1,d[j][2])
			m.set(i,2,d[j][3])
			m.set(i,3,d[j][4])
			m.set(i,4,d[j][5])
			m.set(i,5,d[j][6])
			m.set(i,6,d[j][7])
			#print (h,d)
			e.append(h[j])
			i += 1

	logging.info (m.writeWMaxima('m'))

	mm = m.t_copy().mul_matrix(m)
	logging.info ('transpose(m).m;')
	logging.info (mm.writeWMaxima('mm'))
		
	vb = m.t_copy().mul_vektor(e)
	logging.info ('e:matrix(' + str(e) + ');')
	logging.info ('transpose(m).e');
	mWx = mm.copy().appendCol(vb)
	logging.info (mWx.writeWMaxima('mt'))
	logging.info ('linsolve(maplist(first,mt.[wx,wy,wz,tx,ty,tz,s,1]),[wx,wy,wz,tx,ty,tz,s]);')

	#ee = mm.gauss(vb)
	ee = mm.cholesky(vb)
	logging.info ('ee: ' + str(ee))
	
	w = {1: w[1] + ee[0] , 2: w[2] + ee[1] , 3: w[3] + ee[2] , 4: w[4] + ee[3] , 5: w[5] + ee[4] , 6: w[6] + ee[5] , 7: w[7] + ee[6] }
	logging.info ('w: ' + str(w))
	logging.info ('p: ' + str(pointsCo))

##
##t=[h]
##
##print ("ergH", h)
##print ("ergD", d)
##m.write()
##print ()
##ma = m.t_copy().mul_matrix(m)
##ma.write()
##print ()
##vb = m.t_copy().mul_vektor(t)
##print (vb)
##
##print ()
##ee = ma.gauss(vb)
##print (ee)

# mc = matrix()
# mc.set(0,0,5)
# mc.set(0,1,7)
# mc.set(0,2,3)
# mc.set(1,0,7)
# mc.set(1,1,11)
# mc.set(1,2,2)
# mc.set(2,0,3)
# mc.set(2,1,2)
# mc.set(2,2,6)
# logging.info (mc.writeWMaxima('mc'))

# ee = mc.cholesky([0,0,1])
  
# mc1 = matrix()
# mc1.set(0,0,25)
# mc1.set(0,1,-5)
# mc1.set(0,2,15)
# mc1.set(1,0,-5)
# mc1.set(1,1,10)
# mc1.set(1,2,-15)
# mc1.set(2,0,15)
# mc1.set(2,1,-15)
# mc1.set(2,2,29)
# logging.info (mc1.writeWMaxima('mc1'))  
# ee = mc1.cholesky([0,0,1])

mc2 = matrix()
mc2.set(0,0,9)
mc2.set(0,1,3)
mc2.set(0,2,-6)
mc2.set(0,3,12)

mc2.set(1,0,3)
mc2.set(1,1,26)
mc2.set(1,2,-7)
mc2.set(1,3,-11)

mc2.set(2,0,-6)
mc2.set(2,1,-7)
mc2.set(2,2,9)
mc2.set(2,3,7)

mc2.set(3,0,12)
mc2.set(3,1,-11)
mc2.set(3,2,7)
mc2.set(3,3,65)
logging.info (mc2.writeWMaxima('mc2'))  
#ee = mc2.gauss([72,34,22,326])
#logging.info ('gauss: ' + str(ee))  
ee = mc2.cholesky([72,34,22,326])
logging.info ('cholesky: ' + str(ee))  


