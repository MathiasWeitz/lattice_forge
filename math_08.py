# -*- coding: cp1252 -*-
from math import *
import logging, random
fformat = "%6.7f"


class matrix:
	def __init__(self):
		self.field = [[0]]

	def set(self,y,x,value):
		while len(self.field) <= y:
			self.field.append([0.0])
		while len(self.field[y]) <= x:
			self.field[y].append(0.0)
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
					s = 0.0
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

	def cholesky_old(self, e):
		#logging.info(self.writeWMaxima('chol_s'))
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
		#logging.info(l.writeWMaxima('chol_l'))
		c = []
		for i in range(len(e)):
			s = e[i]
			for j in range(i):
				s -= l.get(i,j) * c[j]
			c.append(s / l.get(i,i))
		#logging.info(c)
		x = [0] * len(c)
		for i in range(len(e)-1,-1,-1):
			s = c[i]
			for k in range(i+1, len(e)):
				s += l.get(k,i) * x[k]
			x[i] = -s / l.get(i,i)
		#logging.info('x: ' + str(x))
		return x
		
	def cholesky(self, e):
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
			s = -e[i]
			for j in range(i):
				s -= l.get(i,j) * c[j]
			if abs(l.get(i,i)) < 1e-12: 
				c.append(0.0)
				logging.info('1:appending 0\n')
			else:
				c.append(s / l.get(i,i))
		logging.info(c)
		x = [0.0] * len(c)
		for i in range(len(e)-1,-1,-1):
			s = c[i]
			for k in range(i+1, len(e)):
				s += l.get(k,i) * x[k]
			if 1e-12 < abs(l.get(i,i)): 
				x[i] = -s / l.get(i,i)
		logging.info(x)
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

logging.basicConfig(filename='c:\\tmp\\python.log', format='%(message)s', level=logging.INFO)

logging.info ("\n***************\n")

logging.info ("define(P(p),matrix([p[1],p[2],p[3]]));")
logging.info ("define(V(v),matrix([v[1],v[2],v[3]]));")
logging.info ("define(PV(p,v), P(p).V(v));")
logging.info ("define(VV(v), sqrt(V(v).V(v)));")
logging.info ("define(h(p,v), PV(p,v)/VV(v) - VV(v));")
logging.info ("define(h_dx(p,v), diff(PV(p,v)/VV(v) - VV(v),v[1]));")
logging.info ("define(h_dy(p,v), diff(PV(p,v)/VV(v) - VV(v),v[2]));")
logging.info ("define(h_dz(p,v), diff(PV(p,v)/VV(v) - VV(v),v[3]));")
	
pointsCo = [
{ 'x':  0.5, 'y':  0.5, 'z': 1.5 },
{ 'x':  0.5, 'y': -0.5, 'z': 1.5 },
{ 'x': -0.5, 'y':  0.5, 'z': 1.5 },
{ 'x': -0.5, 'y': -0.5, 'z': 1.5 },
]	

pointsCo = [
{ 'x':  0.35355335, 'y': -0.5, 'z': -0.35355335 },
{ 'x': -0.35355335, 'y': -0.5, 'z':  0.35355335 },
{ 'x':  0.35355335, 'y':  0.5, 'z': -0.35355335 },
{ 'x': -0.35355335, 'y':  0.5, 'z':  0.35355335 },
]	

v_x , v_y , v_z = 1.1, 1.3, 1.7

rep = 1
while 0 < rep:
	rep -= 1
	m = matrix()
	e = []
	i = 0
	for co in pointsCo:
		arg = '[' + str(co['x']) + ',' + str(co['y']) + ',' + str(co['z']) + '],[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + ']'
		#print (h,d)
		#print (co)
		dot_prod = v_x * co['x'] + v_y  * co['y'] + v_z * co['z']
		#print ('dot_prod',dot_prod)
		#vv = co['x'] * co['x'] + co['y']  * co['y'] + co['z'] * co['z']
		vv = v_x * v_x + v_y  * v_y + v_z * v_z
		v = sqrt(vv)
		# targetValue
		sign = 1.0
		if dot_prod < 0:
			sign = -1.0
		h = dot_prod / v - sign * v
		e.append(-h)
		# derivatives
		dx = co['x'] / v - v_x * (dot_prod / (vv * v) + sign / v)
		dy = co['y'] / v - v_y * (dot_prod / (vv * v) + sign / v)
		dz = co['z'] / v - v_z * (dot_prod / (vv * v) + sign / v)
		logging.info ('h_dx(' + arg + ')  :  '  + str(dx))
		logging.info ('h_dy(' + arg + ')  :  '  + str(dy))
		logging.info ('h_dz(' + arg + ')  :  '  + str(dz))
		m.set(i,  0, dx)
		m.set(i,  1, dy)
		m.set(i,  2, dz)
		i += 1

	logging.info (m.writeWMaxima('m'))

	mm = m.t_copy().mul_matrix(m)
	#logging.info ('transpose(m).m;')
	logging.info (mm.writeWMaxima('mm'))
		
	vb = m.t_copy().mul_vektor(e)
	logging.info ('e:matrix(' + str(e) + ');\n')
	logging.info ('vb:matrix(' + str(vb) + ');\n')
	#logging.info ('transpose(m).e');
	mWx = mm.copy().appendCol(vb)
	logging.info (mWx.writeWMaxima('mt'))
	logging.info ('linsolve(maplist(first,mt.[wx,wy,wz,-1]),[wx,wy,wz]);')

	#eeg = mm.copy().gauss(vb)
	ee = mm.cholesky(vb)
	#logging.info ('eeg: ' + str(eeg))
	logging.info ('ee:matrix(' + str(ee) + ')')
	
	v_x += ee[0]
	v_y += ee[1]
	v_z += ee[2]
	
	logging.info ('v: ' + str(v_x) + ',' + str(v_y) + ',' + str(v_z))
	
	#w = {1: w[1] + ee[0] , 2: w[2] + ee[1] , 3: w[3] + ee[2] , 4: w[4] + ee[3] , 5: w[5] + ee[4] , 6: w[6] + ee[5] , 7: w[7] + ee[6] }
	#logging.info ('w: ' + str(w))
	#logging.info ('p: ' + str(pointsCo))

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

#mc2 = matrix()
#mc2.set(0,0,9)
#mc2.set(0,1,3)
#mc2.set(0,2,-6)
#mc2.set(0,3,12)

#mc2.set(1,0,3)
#mc2.set(1,1,26)
#mc2.set(1,2,-7)
#mc2.set(1,3,-11)

#mc2.set(2,0,-6)
#mc2.set(2,1,-7)
#mc2.set(2,2,9)
#mc2.set(2,3,7)

#mc2.set(3,0,12)
#mc2.set(3,1,-11)
#mc2.set(3,2,7)
#mc2.set(3,3,65)
#logging.info (mc2.writeWMaxima('mc2'))  
#ee = mc2.gauss([72,34,22,326])
#logging.info ('gauss: ' + str(ee))  
#ee = mc2.cholesky([72,34,22,326])
#logging.info ('cholesky: ' + str(ee))  

logging.info ("\n\n############ Test \n")

m = matrix()
for i1 in range(5):
	for i2 in range(3):
		m.set( i1,  i2, 10.0*random.random() - 5.0)

logging.info (m.writeWMaxima('m'))

mm = m.t_copy().mul_matrix(m)
x = [11.0, 17.0, 23.0]

y = mm.t_copy().mul_vektor(x)


#logging.info ('transpose(m).m;')
logging.info (mm.writeWMaxima('mm'))
logging.info ('x:matrix(' + str(x) + ');')
logging.info ('y:matrix(' + str(y) + ');')

mWx = mm.copy().appendCol(y)
logging.info (mWx.writeWMaxima('mt'))
logging.info ('linsolve(maplist(first,mt.[wx,wy,wz,-1]),[wx,wy,wz]);')
	
ee = mm.cholesky(y)
#logging.info ('eeg: ' + str(eeg))
logging.info ('ee:matrix(' + str(ee) + ')')	
	
#logging.info (mm.writeWMaxima('mm'))
#logging.info ('x:matrix(' + str(x) + ');'))


#vb = [878.0, 1035.0, 1498.0]

#logging.info ('vb:matrix(' + str(vb) + ');')
#mWx = mm.copy().appendCol(vb)
#logging.info (mWx.writeWMaxima('mt'))
#logging.info ('linsolve(maplist(first,mt.[wx,wy,wz,-1]),[wx,wy,wz]);')

#ee = mm.cholesky(vb)
#logging.info ('ee:matrix(' + str(ee) + ');')

logging.info ("\n\n############ Test \n")

m = matrix()
m.set( 0,  0, 16.0)
m.set( 0,  1,  4.0)
m.set( 0,  2,  4.0)
m.set( 0,  3, -4.0)

m.set( 1,  0, 4.0)
m.set( 1,  1, 10.0)
m.set( 1,  2, 4.0)
m.set( 1,  3, 2.0)

m.set( 2,  0, 4.0)
m.set( 2,  1, 4.0)
m.set( 2,  2, 6.0)
m.set( 2,  3, -2.0)

m.set( 3,  0, -4.0)
m.set( 3,  1, 2.0)
m.set( 3,  2, -2.0)
m.set( 3,  3, 4.0)


y = [32.0, 26.0, 20.0, -6.0]

logging.info (m.writeWMaxima('m'))
logging.info ('y:matrix(' + str(y) + ');')

mWx = m.copy().appendCol(y)
logging.info (mWx.writeWMaxima('mt'))
logging.info ('linsolve(maplist(first,mt.[wx,wy,wz,-1]),[wx,wy,wz]);')

ee = m.cholesky(y)
logging.info ('ee: ' + str(ee))


