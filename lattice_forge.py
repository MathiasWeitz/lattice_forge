# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
	'name': "Lattices Forge",
	'author': "Mathias Weitz",
	'version': (2, 0, 2),
	'blender': (2, 7, 0),
	'location': "View3D > Tools",
	'description': "several tools for lattices",
	'category': 'Lattice'}

import bpy
from bpy.props import *
import math, time, logging
import mathutils
from math import pi,sin,cos,sqrt
from mathutils import Vector, Matrix

def myHooks_get():
	con = []
	# list of all Vertexgroups
	for o in bpy.context.scene.objects:
		if o.type == 'MESH':
			for ov in o.vertex_groups:
				#print ('Mesh: ', o.name, ov.name, ov.index)
				if ov.name[0:4] == "bnd_":
					con.append({'boundingObject': o, 'boundingVertexgroup': ov})

	# list of all Empties with Copy Location to a Vertexgroup
	for o in bpy.context.scene.objects:
		if o.type == 'EMPTY':
			for oc in o.constraints:
				if oc.name == "Copy Location" and oc.target.type == "MESH" and 3 < len(oc.subtarget):
					for i in range(len(con)):
						elem = con[i]
						#print (i, elem['boundingObject'] == oc.target, elem['boundingVertexgroup'].name == oc.subtarget)
						if elem['boundingObject'] == oc.target and elem['boundingVertexgroup'].name == oc.subtarget:
							#print ('Empty: ', o.name, "Name=", oc.name, ";", oc.target.type, oc.target.name, oc.subtarget, len(oc.subtarget))
							elem['empty'] = o

	# list of all Surface Points with an Hook to an Empty
	for o in bpy.context.scene.objects:
		if o.type == 'SURFACE' or o.type == 'LATTICE':
			for om in o.modifiers:
				if om.type == 'HOOK':
					hookPoints = []
					if bpy.context.active_object != None:
						bpy.ops.object.mode_set(mode = "OBJECT")
					#bpy.ops.object.select_name(name = o.name)
					bpy.ops.object.select_pattern(pattern = o.name, case_sensitive=True, extend=False)
					bpy.ops.object.mode_set(mode = "EDIT")
					#print ('Modifier: ', om.object.name)
					bpy.ops.object.hook_select(modifier = om.name)
					#print (o.data)
					if o.type == 'SURFACE':
						for ospl in o.data.splines:
							for opoi in ospl.points:
								if opoi.select:
									hookPoints.append(opoi)
					else:
						pass
						#for opoi in o.data.points:
						#   if opoi.select:
						#   hookPoints.append(opoi)
					for i in range(len(con)):
						#print ("***** Test " , i)
						elem = con[i]
						if 'empty' in elem and om.object == elem['empty']:
							con[i]['target'] = o
							con[i]['points'] = hookPoints
							con[i]['modifier'] = om

					#print ("Hook", om.name, len(hookPoints))

					#print ('hp=', om.object.name, hookPoints)
	#print ('con = ', con)
	return con

def myHooks_add(active):
	con = myHooks_get()
	# testing the splines
	bpy.ops.object.mode_set(mode = "OBJECT")
	#bpy.ops.object.select_name(name = active.name)
	bpy.ops.object.select_pattern(pattern = active.name, case_sensitive=True, extend=False)
	bpy.ops.object.mode_set(mode = "EDIT")
	points = []
	ma = active.matrix_basis
	maloc = active.location
	mascale = active.scale
	if active.type == 'SURFACE':
		for splines in active.data.splines:
			for w in splines.points:
				points.append(w)
	else:
		for w in active.data.points:
			points.append(w)
	#print ("points", points)
	for w in points:
		hooks = []
		for i in range(len(con)):
			elem = con[i]
			if 'target' in elem and 'points' in elem and active == elem['target'] and w in elem['points']:
				#print ('bounding_vertexgroup', elem['boundingVertexgroup'].name)
				hooks.append(elem)

		#print ("len Hooks", len(hooks))
		if len(hooks) == 0:
			# in w is the point

			# bestes Mesh
			co = w.co
			co = co.to_3d()
			co = Vector((co.x * mascale.x, co.y * mascale.y, co.z * mascale.z)) + maloc
			if active.type == 'LATTICE':
				co = w.co_deform
			bestco = co
			bestD = 5.0
			bestPoint = None
			bestMeshObj = None
			for o in bpy.context.scene.objects:
				if o != bpy.context.active_object and o.type == 'MESH':
					for v in o.data.vertices:
						cov = (o.matrix_basis * v.co.to_4d()).to_3d()
						#print (o.name, cov, (co.to_3d() - cov).length)
						if (co.to_3d() - cov).length < bestD:
							bestD = (co.to_3d() - cov).length
							bestco = cov
							bestPoint = v
							bestMeshObj = o
			#print ("bestD", bestD, bestMeshObj)
			if bestMeshObj != None:
				if active.type == 'SURFACE':
					bestco -= maloc
					bestco = Vector((bestco.x / mascale.x, bestco.y / mascale.y, bestco.z / mascale.z))
					bestco = bestco.to_4d()
					w.co = bestco
				else:
					bestco = bestco.to_3d()
					w.co_deform = bestco

				vg = bestMeshObj.vertex_groups.new(name = "bnd_vgroup")
				vg.add([bestPoint.index], 1.0, "ADD")

				# Empty erzeugen
				emptyObj = bpy.data.objects.new("bnd_conObj", None)
				emptyObj.hide = True
				bpy.context.scene.objects.link(emptyObj)
				cs = emptyObj.constraints.new('COPY_LOCATION')
				cs.target = bestMeshObj
				cs.subtarget = vg.name

				# Hook erzeugen
				hook = active.modifiers.new(name = 'bnd_hook', type = 'HOOK')
				hook.object = emptyObj
				hook.show_in_editmode = True
				if active.type == 'SURFACE':
					for w0 in points:
						w0.select = w == w0
				else:
					# TODO: this kind of selection is just dead ugly
					# it should be replaced by something else as soon as possible
					tmpGrp = active.vertex_groups.new(name = "bnd_tmp")
					bpy.ops.lattice.select_all(action = 'DESELECT')
					#bpy.ops.object.mode_set(mode = "OBJECT")
					bpy.ops.object.vertex_group_set_active(group = tmpGrp.name)
					for i in range(len(active.data.points)):
						#print (i, active.data.points[i].co, w.co, (active.data.points[i].co - w.co).length)
						if (active.data.points[i].co - w.co).length < 0.0001:
							#print ("adding", tmpGrp.name, i)
							bpy.ops.object.mode_set(mode = "OBJECT")
							tmpGrp.add([i],1.0,'REPLACE')
							bpy.ops.object.mode_set(mode = "EDIT")
					#bpy.ops.object.mode_set(mode = "EDIT")
					bpy.ops.object.vertex_group_select()
					active.vertex_groups.remove(tmpGrp)
				bpy.ops.object.hook_assign(modifier = hook.name)
				bpy.ops.object.hook_reset(modifier = hook.name)
	bpy.ops.object.mode_set(mode = "OBJECT")

def myHooks_apply(active, apply = True):
	con = myHooks_get()
	bpy.ops.object.mode_set(mode = "OBJECT")
	#bpy.ops.object.select_name(name = active.name)
	bpy.ops.object.select_pattern(pattern = active.name, case_sensitive=True, extend=False)
	#bpy.ops.object.mode_set(mode = "EDIT")
	lm = len(active.modifiers)
	#print ("Anzahl Modifiers", lm)
	i = 0
	while i < len(active.modifiers):
		if active.modifiers[i].type == "HOOK":
			#print ("Modifier", i, active.modifiers[i].name)
			is_mod = False
			empty = None
			target = None
			subtarget = None
			for j in range(len(con)):
				elem = con[j]
				if 'target' in elem and 'modifier' in elem and active == elem['target'] and  active.modifiers[i] == elem['modifier']:
					is_mod = True
					empty = elem['empty']
					target = elem['boundingObject']
					subtarget = elem['boundingVertexgroup']
			if is_mod:
				#print ("apply Modifier")
				if apply:
					bpy.ops.object.modifier_apply(apply_as='DATA', modifier=active.modifiers[i].name)
				else:
					bpy.ops.object.modifier_remove(modifier=active.modifiers[i].name)
				#bpy.ops.object.select_name(name = empty.name)
				bpy.context.scene.objects.unlink(empty)
				bpy.data.objects.remove(empty)
				target.vertex_groups.remove(subtarget)

			else:
				i += 1
		else:
			i += 1
	bpy.ops.object.mode_set(mode = "OBJECT")

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
		#print ("mul_vektor", self.dimX(), len(v))
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
			if abs(l.get(i,i)) < 1e-12: 
				c.append(0.0)
			else:
				c.append(s / l.get(i,i))
		#logging.info(c)
		x = [0] * len(c)
		for i in range(len(e)-1,-1,-1):
			s = c[i]
			for k in range(i+1, len(e)):
				s += l.get(k,i) * x[k]
			if 1e-12 < abs(l.get(i,i)): 
				x[i] = -s / l.get(i,i)
		#logging.info(x)
		return x

	def gauss(self, e):
		#print ("********************** lineare Gleichung")
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
			#logging.info (self.writeWMaxima('zf' + str(i)))
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
		#logging.info ('rank: ' + str(rank))
		#if 0 < rank and rank < len(self.field)-1:
		#	subMatrixStart = len(self.field)-rank-1
		#	subMatrix = matrix()
		#	for i1 in range(rank+1):
		#		for i2 in range(rank+1):
		#			subMatrix.set(i1, i2, self.get(i1, i2+subMatrixStart))
		#	#logging.info (subMatrix.writeWMaxima('subm'))
		# backward-Schritt
		lin = False
		for i in range(len(self.field)-1,0,-1):
			#print ("backward",i)
			#self.write()
			#print (e)
			#logging.info (self.writeWMaxima('zb' + str(i)))
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

def spline (ai, steps, mode = 1, smode = 0, usegs = []):
		# ai ist eine Array von Koordinatenwerten (in einem Array)
		# mode:
		#  1 = normaler Spline
		#  2 = circularer Spline
		# smode:
		#  0 = Subdivide
		#  1 = gleichmaessige Aufteilung
		#  2 = Aufteilung nach der Menge der Punkte in usegs

	#logging.info('start spline time: ' + str(time.time()))
	if len(ai) == len(usegs):
		# falls ein geschlossener Kantenzug vorliegt, dann
		# ist der Spline auf jeden Fall circular
		mode = 2
		
	preIndex = 0
	if mode == 2:
		ai.append(ai[0])
		ai.append(ai[1])
		preIndex = 1
	h = []
	sumh = 0.0
	for i in range(len(ai)-1):
		dx,dy,dz = ai[i][0] - ai[i+1][0], ai[i][1] - ai[i+1][1], ai[i][2] - ai[i+1][2]
		d = sqrt(dx*dx + dy*dy + dz*dz)
		h.append(d)
		if mode==1 or mode==3 or i < len(ai) - 2:
			sumh += d

	count_curves = len(ai[0])
	erg = [[] for k in range(count_curves)]
	ergTest = [[] for k in range(count_curves)]
	splines_tm = []
	#logging.info('erg ' + str(erg))
	
	#print(ai)
	for v in range(count_curves):
		#logging.info ("\n****** Koordinate " + str(v))
		m = matrix()
		e = []
		werta = []
		for i in range(len(ai)):
			werta.append(ai[i][v])
		if mode==1 or mode==2:
			for i in range(len(h)-2):
				m.set(i,i+1,h[i+1])
				m.set(i+1,i,h[i+1])
				m.set(i,i,2*(h[i] + h[i+1]))
				m.set(i+1,i+1,2*(h[i+1] + h[i+2]))
			if mode == 2:
				# Zusatz für circulare Splines
				m.set(0,len(h)-2, m.get(0, len(h)-2) + h[0])
				m.set(len(h)-2, 0, m.get(len(h)-2, 0) + h[0])

			for i in range(len(h)-1):
				e.append(3/h[i+1] * (werta[i+2]-werta[i+1]) - 3/h[i] * (werta[i+1]-werta[i]))

			wertc1 = m.copy().gauss(e)

			if mode==1:
				# regulaer
				wertc = [0.0]
			elif mode==2:
				# circular
				wertc = [wertc1[len(wertc1)-1]]
			else:
				pass
			for c in wertc1:
				wertc.append(c)
			if mode==1:
				# regulaer
				wertc.append(0.0)
			elif mode==2:
				# circular
				werta.append(werta[1])
			else:
				pass

		wertd = []
		wertb = []
		for i in range(len(h)-preIndex):
			b = 1.0/h[i] * (werta[i+1]-werta[i]) - h[i]/3.0 * (wertc[i+1]+2.0*wertc[i])
			wertb.append(b)
			wertd.append(1.0/h[i] * (wertc[i+1]-wertc[i]) / 3.0)

		#print ("a", werta)
		#print ("b", wertb)
		#print ("c", wertc)
		#print ("d", wertd)

		if smode == 0:
			# subdivide
			for i in range(len(ai)-1):
				erg[v].append(ai[i][v])
				for j in range(1,steps):
					jv = 1.0 * j / steps * h[i]
					value = werta[i] + jv*wertb[i] + jv*jv*wertc[i] + jv*jv*jv*wertd[i]
					erg[v].append(value)
					#print (0.0 + i + jv, value)
			erg[v].append(ai[len(ai)-1][v])

		if smode == 1:
			# stepsh is the internal resolution of the splines
			# the more steps you take the more accurate your result will be,
			# but also it will take more time to rebalance
			#logging.info('start making steps: ' + str(time.time()))
			#stepsh = 250000
			tm = []
			for i in range(len(ai)-1):
				tm.append({'werta': werta[i], 'wertb':wertb[i], 'wertc':wertc[i], 'wertd':wertd[i], 'h':h[i]})
			#logging.info('tm: ' + str(tm))
			#for ii in range(0,4 * len(ai)):
			#	i = ii / 4.0
			#	#logging.info('tmi: ' + str(i) + ' ' + str(getSplineValue(i,tm)) )
			splines_tm.append(tm)
			#for i in range(len(ai)-1):
			#	ergTest[v].append(ai[i][v])
			#	for j in range(1,stepsh):
			#		jv = 1.0 * j / stepsh * h[i]
			#		value = werta[i] + jv*wertb[i] + jv*jv*wertc[i] + jv*jv*jv*wertd[i]
			#		ergTest[v].append(value)
			#		#print (0.0 + i + jv, value)
			#ergTest[v].append(ai[len(ai)-1][v])
			#logging.info('values: ' + str(tm))
			#logging.info('end making steps: ' + str(time.time()))

	if smode == 1:
		#logging.info('start realign time: ' + str(time.time()))
		#print ('len ai', len(ai), len(tm), steps)
		st = (len(ai)-1) / (steps-1)
		#print ('st', st)
		ma = [i * st for i in range(steps)]
		std = 0.25 * st
		c = 5000
		tdel = [9999.9 for k in range(3)]
		while 0 < c:
			c -= 1
			#print ('ma', ma)
			d = []
			for mai in ma:
				#ptest = "%5.3f" % mai + ': '
				xspl, yspl, zspl = splines_tm[0],splines_tm[1],splines_tm[2]
				d.append([getSplineValue(mai, xspl),getSplineValue(mai, yspl),getSplineValue(mai, zspl)])
				#ptest += "%9.5f" % getSplineValue(mai, mat)
				#print (ptest)
			ind_min, ind_max = 0, 0
			value_min, value_max = 10000000.0, -1.0
			for i in range(len(ma)-1):
				dx, dy, dz = d[i][0] - d[i+1][0], d[i][1] - d[i+1][1],d[i][2] - d[i+1][2]
				hh = sqrt(dx*dx + dy*dy + dz*dz)
				#print (i, hh)
				if hh < value_min:
					value_min = hh
					ind_min = i
				if value_max < hh:
					value_max = hh
					ind_max = i
			max_diff = value_max - value_min
			tdel.append(max_diff)
			last = tdel.pop(0)
			if last <= max_diff:
				std = max(std*0.5,1e-7)
				tdel.append(9999.9)
			#print (c,std, ind_min, ind_max, max_diff)
			if 1e-5 < max_diff:
				dir = 1
				if ind_max < ind_min:
					dir = -1
				for i in range(min(ind_min,ind_max)+1,max(ind_min,ind_max)+1):
					ma[i] += dir * std
			else:
				c = 0
		#print (ma)
		for im in range(len(ma)):
			for v in range(count_curves):
				erg[v].append(getSplineValue(ma[im], splines_tm[v]))
		if False:
			#die alte Variante des Ausgleichs
			dd = 8192
			tdel = [9999.9 for k in range(25)]
			m = [0] + [int(len(ergTest[0]) * i / (steps-1)) for i in range(1,steps-1)] + [len(ergTest[0]) - 1]
			#for i in range(len(ergTest[0])-1):
			#   dx,dy,dz = ergTest[0][i+1] - ergTest[0][i], ergTest[1][i+1] - ergTest[1][i], ergTest[2][i+1] - ergTest[2][i]
			#   h = math.sqrt(dx*dx + dy*dy + dz*dz)
			#   #print (h)
			#print (m)
			# maximum steps for rebalancing
			c = 999999
			while 0 < c:
				c -= 1
				ind_min, ind_max = 0, 0
				value_min, value_max = 10000000.0, -1.0
				for im in range(len(m)-1):
					dx = ergTest[0][m[im+1]] - ergTest[0][m[im]]
					dy = ergTest[1][m[im+1]] - ergTest[1][m[im]]
					dz = ergTest[2][m[im+1]] - ergTest[2][m[im]]
					d = math.sqrt(dx*dx + dy*dy + dz*dz)
					if d < value_min:
						value_min = d
						ind_min = im
					if value_max < d:
						value_max = d
						ind_max = im
				#if c%100000 == 0:
				moveDir = 0
				if 0.001 < value_max - value_min or 0 < dd:
					max_diff = value_max - value_min
					#print ("%5.7f" % (max_diff))
					moveDir = dd
					ran = range(ind_min,ind_max)
					if ind_max < ind_min:
						moveDir = -max(1,min(dd, (m[ind_min+1] - m[ind_min]) // 2))
						ran = range(ind_max,ind_min)
					else:
						moveDir = max(1,min(dd, (m[ind_max+1] - m[ind_max]) // 2))
					#logging.info ('min, max, ran, moveDir ' + str(ind_min) + ' ' + str(ind_max) + ' ' + str(ran) + ' ' + str(moveDir))
					for im in ran:
						m[im+1] += moveDir
					tdel.append(max_diff)
					last = tdel.pop(0)
					if 0 < dd and last <= max_diff:
						dd = dd // 2
				else:
					#print ('end', c) 
					if dd == 0:
						c = 0
					else:
						dd = dd // 2
						tdel = [9999.9 for k in range(25)]
				#logging.info ("%6d" % c + "%5d" % moveDir + " " + "%5.7f" % (value_max - value_min) + " " + "%2u" % ind_min + " " + "%2u" % ind_max + " : " + "%5.7f" % tdel[0] + " ... " + "%5.7f" % tdel[-1] + " " + str(m))
			#print (m)
			for im in range(len(m)):
				for v in range(count_curves):
					erg[v].append(ergTest[v][m[im]])
		#print ('***************************')
	#logging.info('spline-erg: ' + str(erg))

#
#   #print
#   #print (len(erg[0]))
	#logging.info('end spline time: ' + str(time.time()))
	return erg

def getSplineValue(x, splineData):
	# last Index
	i = min(int(x), len(splineData)-1)
	jv = (x - i) * splineData[i]['h']
	value = splineData[i]['werta'] + jv*splineData[i]['wertb'] + jv*jv*splineData[i]['wertc'] + jv*jv*jv*splineData[i]['wertd']
	return value
	
class point:
	point = {}
	def __init__(self, point):
		self.point = point
		
	def coor(self):
		return self.point

class trajectory:
	point = {}
	offset = {1: 0.0, 2:0.0, 3:0.0}
	w = {1: 0.0, 2:0.0, 3:0.0}
	trajectoryPoint = None
	verbose = 0
	h = 0.0
	diff = (0.0, 0.0, 0.0)
	isCalculated = False

	def __init__(self, point):
		self.point = point

	def setTrajectoryPoint(self, point):
		self.trajectoryPoint = point
		
	def setRotation(self, w):
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
		
	def getTrajectoryPoint(self):
		self.calculate()
		return self.trajectoryPoint
		
	def log(self, text = ''):
		logging.info(text)
		return self
		with open('lattice_untorsion_log.txt', 'a') as f:
			f.write(text + '\n')
		#f = open(savename, 'a')
		#pickle.dump(cop,f)
		f.close()

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
			# Rotationmatrix
			vp[1] = v[3]*(sin(w[1])*sin(w[3])-cos(w[1])*sin(w[2])*cos(w[3]))+v[2]*(-cos(w[1])*sin(w[3])-sin(w[1])*sin(w[2])*cos(w[3]))+v[1]*cos(w[2])*cos(w[3])
			vp[2] = v[2]*(cos(w[1])*cos(w[3])-sin(w[1])*sin(w[2])*sin(w[3]))+v[3]*(-cos(w[1])*sin(w[2])*sin(w[3])-sin(w[1])*cos(w[3]))+v[1]*cos(w[2])*sin(w[3])
			vp[3] = v[1]*sin(w[2])+v[2]*sin(w[1])*cos(w[2])+v[3]*cos(w[1])*cos(w[2])

			# Derivative of the Rotationmatrix
			Mp_diffx = {1: v[2]*(sin(w[1])*sin(w[3])-cos(w[1])*sin(w[2])*cos(w[3]))+v[3]*(cos(w[1])*sin(w[3])+sin(w[1])*sin(w[2])*cos(w[3])), \
				2: v[3]*(sin(w[1])*sin(w[2])*sin(w[3])-cos(w[1])*cos(w[3]))+v[2]*(-cos(w[1])*sin(w[2])*sin(w[3])-sin(w[1])*cos(w[3])), \
				3: v[2]*cos(w[1])*cos(w[2])-v[3]*sin(w[1])*cos(w[2])}

			Mp_diffy = {1: -v[1]*sin(w[2])*cos(w[3])-v[2]*sin(w[1])*cos(w[2])*cos(w[3])-v[3]*cos(w[1])*cos(w[2])*cos(w[3]), \
				2: -v[1]*sin(w[2])*sin(w[3])-v[2]*sin(w[1])*cos(w[2])*sin(w[3])-v[3]*cos(w[1])*cos(w[2])*sin(w[3]), \
				3: -v[2]*sin(w[1])*sin(w[2])-v[3]*cos(w[1])*sin(w[2])+v[1]*cos(w[2])}

			Mp_diffz = {1: v[2]*(sin(w[1])*sin(w[2])*sin(w[3])-cos(w[1])*cos(w[3]))+v[3]*(cos(w[1])*sin(w[2])*sin(w[3])+sin(w[1])*cos(w[3]))-v[1]*cos(w[2])*sin(w[3]), \
						2: v[3]*(sin(w[1])*sin(w[3])-cos(w[1])*sin(w[2])*cos(w[3]))+v[2]*(-cos(w[1])*sin(w[3])-sin(w[1])*sin(w[2])*cos(w[3]))+v[1]*cos(w[2])*cos(w[3]), \
						3: 0}

			vpx2,vpy2,vpz2 = vp[1]*vp[1], vp[2]*vp[2], vp[3]*vp[3]
			distz = sqrt(vpx2 + vpy2 + vpz2)
			normz = {1:vp[1]/distz,2:vp[2]/distz,3:vp[3]/distz}
			# just for calculation, the distance of a vector in a rotationmatrix never changes
			distz_diffx = 0.0
			distz_diffy = 0.0
			distz_diffz = 0.0

			normz_diffx = {1: Mp_diffx[1] / distz, 2: Mp_diffx[2] / distz, 3: Mp_diffx[3] / distz}
			normz_diffy = {1: Mp_diffy[1] / distz, 2: Mp_diffy[2] / distz, 3: Mp_diffy[3] / distz}
			normz_diffz = {1: Mp_diffz[1] / distz, 2: Mp_diffz[2] / distz, 3: Mp_diffz[3] / distz}
			
			# difference to the trajecting point (this is vector two we do refer to)
			zug = {1:vp[1] - p[1],2:vp[2] - p[2],3:vp[3] - p[3]}
			zugx2,zugy2,zugz2 = zug[1]*zug[1], zug[2]*zug[2], zug[3]*zug[3]
			distzug = sqrt(zugx2 + zugy2 + zugz2)
			normzug = {1:zug[1]/distzug,2:zug[2]/distzug,3:zug[3]/distzug}

			# dot-product 
			prod = zug[1] * vp[1] + zug[2] * vp[2] + zug[3] * vp[3]
			
			# both distances multiplied
			prod_dist = distzug * distz
			# cos of both vectors (= normed dot product) + 1
			# this is the targeting result, this should get zero
			target = prod / (prod_dist) + 1

			# derivative of trajecting point
			distzug_diffx = (zug[1] * Mp_diffx[1] + zug[2] * Mp_diffx[2] + zug[3] * Mp_diffx[3]) / distzug
			distzug_diffy = (zug[1] * Mp_diffy[1] + zug[2] * Mp_diffy[2] + zug[3] * Mp_diffy[3]) / distzug
			distzug_diffz = (zug[1] * Mp_diffz[1] + zug[2] * Mp_diffz[2] + zug[3] * Mp_diffz[3]) / distzug

			# derivative of the dot-product
			prod_diffx = (2*vp[1] - p[1]) * Mp_diffx[1] + (2*vp[2] - p[2]) * Mp_diffx[2] + (2*vp[3] - p[3]) * Mp_diffx[3]
			prod_diffy = (2*vp[1] - p[1]) * Mp_diffy[1] + (2*vp[2] - p[2]) * Mp_diffy[2] + (2*vp[3] - p[3]) * Mp_diffy[3]
			prod_diffz = (2*vp[1] - p[1]) * Mp_diffz[1] + (2*vp[2] - p[2]) * Mp_diffz[2] + (2*vp[3] - p[3]) * Mp_diffz[3]

			# derivative of the distance-product (prod_dist)
			prod_dist_diffx = distzug_diffx * distz
			prod_dist_diffy = distzug_diffy * distz
			prod_dist_diffz = distzug_diffz * distz

			# derivative of target
			target_diff = {}
			target_diff[1] = (prod_diffx * prod_dist - prod_dist_diffx * prod) / (prod_dist * prod_dist)
			target_diff[2] = (prod_diffy * prod_dist - prod_dist_diffy * prod) / (prod_dist * prod_dist)
			target_diff[3] = (prod_diffz * prod_dist - prod_dist_diffz * prod) / (prod_dist * prod_dist)

			self.h = target
			self.diff = target_diff
			self.trajectoryPoint = {1: self.offset[1] + vp[1], 2: self.offset[2] + vp[2], 3: self.offset[3] + vp[3]}
			self.isCalculated = True
				
			if 1 == self.verbose:
				# nomenklatura for wxmaxima
				self.log ("load(vect);")
				self.log ("define (Ax(w), matrix([1,0,0],[0,cos(w[1]),-sin(w[1])],[0,sin(w[1]),cos(w[1])]));")
				self.log ("define (Ay(w), matrix([cos(w[2]),0,-sin(w[2])],[0,1,0],[sin(w[2]),0,cos(w[2])]));")
				self.log ("define (Az(w), matrix([cos(w[3]),-sin(w[3]),0],[sin(w[3]),cos(w[3]),0],[0,0,1]));")
				self.log ("define (M(w), Az(w).Ay(w).Ax(w));")
				self.log ("define(V(v),matrix([v[1],v[2],v[3]]));")
				self.log ("define(Mp(w,v), M(w).V(v));")
				self.log ("define(distz(w,v), sqrt(Mp(w,v).Mp(w,v)));")
				self.log ("define(normz(w,v), Mp(w,v)/distz(w,v));")

				self.log ("define(Mp_diffx(w,v), diff(Mp(w,v),w[1]));")
				self.log ("define(Mp_diffy(w,v), diff(Mp(w,v),w[2]));")
				self.log ("define(Mp_diffz(w,v), diff(Mp(w,v),w[3]));")

				self.log ("define(distz_diffx(w,v), diff(distz(w,v),w[1]));")
				self.log ("define(distz_diffy(w,v), diff(distz(w,v),w[2]));")
				self.log ("define(distz_diffz(w,v), diff(distz(w,v),w[3]));")

				self.log ("define(normz_diffx(w,v), diff(normz(w,v),w[1]));")
				self.log ("define(normz_diffy(w,v), diff(normz(w,v),w[2]));")
				self.log ("define(normz_diffz(w,v), diff(normz(w,v),w[3]));")
				
				self.log ("P:[" + str(p[1]) + "," + str(p[2]) + "," + str(p[3]) + "];")
				self.log ("define(zug(w,v), Mp(w,v) - P);")
				self.log ("define(distzug(w,v), sqrt(zug(w,v).zug(w,v)));")
				self.log ("define(distzug_diffx(w,v), diff(distzug(w,v),w[1]));")
				self.log ("define(distzug_diffy(w,v), diff(distzug(w,v),w[2]));")
				self.log ("define(prodp(w,v), zug(w,v).Mp(w,v));")
				self.log ("define(prodDist(w,v), distz(w,v)*distzug(w,v));")
				self.log ("define(target(w,v), prodp(w,v) / prodDist(w,v) + 1);")
				self.log ("define(prod_diffx(w,v), diff(prodp(w,v),w[1]));")
				self.log ("define(prod_diffy(w,v), diff(prodp(w,v),w[2]));")
				self.log ("define(prod_diffz(w,v), diff(prodp(w,v),w[3]));")
				self.log ("define(prod_dist_diffx(w,v), diff(prodDist(w,v),w[1]));")
				self.log ("define(prod_dist_diffy(w,v), diff(prodDist(w,v),w[2]));")
				self.log ("define(prod_dist_diffz(w,v), diff(prodDist(w,v),w[3]));")
				self.log ("define(Target_diffx(w,v), diff(target(w,v),w[1]));")
				self.log ("define(Target_diffy(w,v), diff(target(w,v),w[2]));")
				self.log ("define(Target_diffz(w,v), diff(target(w,v),w[3]));")
				
				self.log()
				arg = '[' + str(w[1]) +  ',' +  str(w[2]) + ',' +  str(w[3]) +'],[' + str(v[1]) + ',' +  str(v[2]) + ',' + str(v[3]) + ']'
				self.log("Mp(" + arg + ") = " + str(vp))
				self.log("Mp_diffx(" + arg + ") = " + str(Mp_diffx))
				self.log("Mp_diffy(" + arg + ") = " + str(Mp_diffy))
				self.log("Mp_diffz(" + arg + ") = " + str(Mp_diffz))
				self.log("distz(" + arg + ") = " + str(distz))
				self.log("normz(" + arg + ") = " + str(normz))
				
				self.log("normz_diffx(" + arg + ") = " + str(normz_diffx))
				self.log("normz_diffy(" + arg + ") = " + str(normz_diffy))
				self.log("normz_diffz(" + arg + ") = " + str(normz_diffz))
				
				self.log ("zug(" + arg + ") = " + str(zug))
				self.log ("distz(" + arg + ") = " + str(distzug))
				self.log ("prodp(" + arg + ") = " + str(prod))
				self.log ("target(" + arg + ") = " + str(target))
				
				self.log ("prodDist(" + arg + ") = " + str(prod_dist))
				self.log ("distzug_diffx(" + arg + ") = " + str(distzug_diffx))
				self.log ("distzug_diffy(" + arg + ") = " +  str(distzug_diffy))
				self.log ("distzug_diffz(" + arg + ") = " + str(distzug_diffz))
				self.log ("prod_diffx(" + arg + ") = " + str(prod_diffx))
				self.log ("prod_diffy(" + arg + ") = " + str(prod_diffy))
				self.log ("prod_diffz(" + arg + ") = " + str(prod_diffz))
				self.log ("prod_dist_diffx(" + arg + ") = " + str(prod_dist_diffx))
				self.log ("prod_dist_diffy(" + arg + ") = " + str(prod_dist_diffy))
				self.log ("prod_dist_diffz(" + arg + ") = " + str(prod_dist_diffz))
				self.log ("Target_diffx(" + arg + ") = " + str(target_diff[1]))
				self.log ("Target_diffy(" + arg + ") = " + str(target_diff[2]))
				self.log ("Target_diffz(" + arg + ") = " + str(target_diff[3]))

class SurfaceBind(bpy.types.Operator):
	'''Binds a Surface or Lattice to the closest points of a Mesh'''
	bl_idname = 'surface.bind'
	bl_label = 'SurfaceBind'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and (obj.type == 'SURFACE' or obj.type == 'LATTICE'))

	def execute(self, context):
		active = bpy.context.active_object
		myHooks_add(active)
		return {'FINISHED'}

class SurfaceApply(bpy.types.Operator):
	'''Applies the Modifiers for a surface'''
	bl_idname = 'surface.apply'
	bl_label = 'SurfaceApply'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'SURFACE')

	def execute(self, context):
		active = bpy.context.active_object
		myHooks_apply(active)
		return {'FINISHED'}

class SurfaceUnbind(bpy.types.Operator):
	'''Delete the Modifiers for a Surface'''
	bl_idname = 'surface.unbind'
	bl_label = 'SurfaceUnbind'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'SURFACE')

	def execute(self, context):
		active = bpy.context.active_object
		myHooks_apply(active, False)
		return {'FINISHED'}

def latticeRemeshBasic(activeLattice,lattice_dir, mode=0, points = 0):
	lu = activeLattice.data.points_u
	lv = activeLattice.data.points_v
	lw = activeLattice.data.points_w
	if lattice_dir == 'u':
		splines = [[[] for i in range(lv)] for j in range(lw)]
		#print(splines)
		for iw in range(lw):
			for iv in range(lv):
				for iu in range(lu):
					i = lu * lv * iw + lu * iv + iu
					#print (i, activeLattice.data.points[i].co)
					splines[iw][iv].append(activeLattice.data.points[i].co_deform)
					#print ('')
		if mode == 1:
			lu = points
		else:
			lu = lu * 2 - 1
		activeLattice.data.points_u = lu
		for iw in range(lw):
			for iv in range(lv):
				#print (iw,iv)
				if mode == 1:
					nv = spline (splines[iw][iv], lu, 1, 1)
				else:
					nv = spline (splines[iw][iv], 2)
				#print (nv)
				ran = range(1,lu,2)
				if mode == 1:
					ran = range(1,lu-1)
				for iu in ran:
					i = lu * lv * iw + lu * iv + iu
					#print (i,iw,iv,iu)
					activeLattice.data.points[i].co_deform.x = nv[0][iu]
					activeLattice.data.points[i].co_deform.y = nv[1][iu]
					activeLattice.data.points[i].co_deform.z = nv[2][iu]
	if lattice_dir == 'v':
		splines = [[[] for i in range(lu)] for j in range(lw)]
		#print(splines)
		for iw in range(lw):
			for iu in range(lu):
				for iv in range(lv):
					i = lu * lv * iw + lu * iv + iu
					#print (i, activeLattice.data.points[i].co)
					splines[iw][iu].append(activeLattice.data.points[i].co_deform)
					#print ('')
		if mode == 1:
			lv = points
		else:
			lv = lv * 2 - 1
		activeLattice.data.points_v = lv
		for iw in range(lw):
			for iu in range(lu):
				#print (iw,iu)
				if mode == 1:
					nv = spline (splines[iw][iu], lv, 1, 1)
				else:
					nv = spline (splines[iw][iu], 2)
				ran = range(1,lv,2)
				if mode == 1:
					ran = range(1,lv-1)
				for iv in ran:
					i = lu * lv * iw + lu * iv + iu
					#print (i,iw,iv,iu)
					activeLattice.data.points[i].co_deform.x = nv[0][iv]
					activeLattice.data.points[i].co_deform.y = nv[1][iv]
					activeLattice.data.points[i].co_deform.z = nv[2][iv]
	if lattice_dir == 'w':
		splines = [[[] for i in range(lu)] for j in range(lv)]
		for iv in range(lv):
			for iu in range(lu):
				for iw in range(lw):
					i = lu * lv * iw + lu * iv + iu
					splines[iv][iu].append(activeLattice.data.points[i].co_deform)
		if mode == 1:
			lw = points
		else:
			lw = lw * 2 - 1
		activeLattice.data.points_w = lw
		for iv in range(lv):
			for iu in range(lu):
				#print (iv,iu)
				if mode == 1:
					nv = spline (splines[iv][iu], lw, 1, 1)
				else:
					nv = spline (splines[iv][iu], 2)
				ran = range(1,lw,2)
				if mode == 1:
					ran = range(1,lw-1)
				for iw in ran:
					i = lu * lv * iw + lu * iv + iu
					activeLattice.data.points[i].co_deform.x = nv[0][iw]
					activeLattice.data.points[i].co_deform.y = nv[1][iw]
					activeLattice.data.points[i].co_deform.z = nv[2][iw]

def latticeRemeshMode(activeLattice,lattice_dir, mode=0):
	points = 0
	if mode == 0:
		if lattice_dir == 'u':
			points = activeLattice.data.points_u
		if lattice_dir == 'v':
			points = activeLattice.data.points_v
		if lattice_dir == 'w':
			points = activeLattice.data.points_w
	if 3 < points:
		latticeRemeshBasic(activeLattice, lattice_dir, 1, points)

class LatticeRemesh(bpy.types.Operator):
	'''add cubic Points in the given direction'''
	bl_idname = 'lattice.latticeremesh'
	bl_label = 'LatticeAddCubic'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if not obj or obj.type != 'LATTICE':
			return False
		return True

	def execute(self, context):
		activeLattice = bpy.context.active_object
		lattice_dir = context.scene.lattice_dir
		#latticeRemeshBasic(activeLattice, lattice_dir, 1, 10)
		latticeRemeshMode(activeLattice, lattice_dir, 0)
		return {'FINISHED'}

class LatticeAddCubic(bpy.types.Operator):
	'''add cubic Points in the given direction'''
	bl_idname = 'lattice.latticeaddcubic'
	bl_label = 'LatticeAddCubic'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if not obj or obj.type != 'LATTICE':
			return False
		lattice_dir = context.scene.lattice_dir
		lu = obj.data.points_u
		lv = obj.data.points_v
		lw = obj.data.points_w
		if lattice_dir == 'u' and lu < 4:
			return False
		if lattice_dir == 'v' and lv < 4:
			return False
		if lattice_dir == 'w' and lw < 4:
			return False
		return True

	def execute(self, context):
		activeLattice = bpy.context.active_object
		lattice_dir = context.scene.lattice_dir
		latticeRemeshBasic(activeLattice, lattice_dir)
		return {'FINISHED'}

class LatticeReBind(bpy.types.Operator):
	'''ReBind a Lattice'''
	bl_idname = 'lattice.rebind'
	bl_label = 'LatticeRebind'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'LATTICE')

	def execute(self, context):
		activeLattice = bpy.context.active_object
		acticeSourceObject = None
		modifierLattice = None
		lattice = None
		# find the right base-object
		for item in bpy.context.scene.objects:
			if item.type == 'MESH':
				#print (item.name, item.type)
				for modifier in item.modifiers:
					if modifier.type == 'LATTICE' and modifier.object == activeLattice:
						acticeSourceObject = item
						modifierLattice = modifier
						lattice = modifier.object
		if acticeSourceObject!=None:
			l = {}
			l['u'] = activeLattice.data.points_u
			l['v'] = activeLattice.data.points_v
			l['w'] = activeLattice.data.points_w
			dimA = ['u','v','w']
			dimAA = {'u':['v','w',0],'v':['u','w',1],'w':['u','v',2]}
			# factors for multiplying
			factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
			# now do a lot of operations
			#print(acticeSourceObject, modifierLattice, modifierLattice.name)
			minv = {'u':  999999, 'v':  999999, 'w':  999999}
			maxv = {'u': -999999, 'v': -999999, 'w': -999999}
			minX, maxX, minY, maxY, minZ, maxZ = 10000, -10000, 10000, -10000, 10000, -10000
			for v in acticeSourceObject.data.vertices:
				#cov = (active.matrix_basis * v.co.to_4d()).to_3d()
				cov = v.co
				#print (o.name, cov, (co.to_3d() - cov).length)
				minv['u'], maxv['u'] = min(minv['u'], cov.x), max(maxv['u'], cov.x)
				minv['v'], maxv['v'] = min(minv['v'], cov.y), max(maxv['v'], cov.y)
				minv['w'], maxv['w'] = min(minv['w'], cov.z), max(maxv['w'], cov.z)
				dx, dy, dz = maxv['u'] - minv['u'], maxv['v'] - minv['v'], maxv['w'] - minv['w']
				dx2, dy2, dz2 = 1.0, 1.0, 1.0
			#bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
			#acticeSourceObject.rotation_euler = mathutils.Euler((0.0, 0.0, 0.0), 'XYZ')
			dd = {}
			pd = {}
			dd['u'] = 1.0
			if abs(dx) < 1e-6:
				pd['u'], dx, dx2 = - minv['u'], 1.0, 0.0
			else:
				dd['u'] = 1.0 / dx
				pd['u'] = - minv['u'] * dd['u'] - 0.5
			dd['v'] = 1.0
			if abs(dy) < 1e-6:
				pd['v'], dy, dy2 = - minv['v'], 1.0, 0.0
			else:
				dd['v'] = 1.0 / dy
				pd['v'] = - minv['v'] * dd['v'] - 0.5
			dd['w'] = 1.0
			if abs(dz) < 1e-6:
				pd['w'], dz, dz2 = - minv['w'], 1.0, 0.0
			else:
				dd['w'] = 1.0 / dz
				pd['w'] = - minv['w'] * dd['w'] - 0.5
			#print (minX, new_active.location.x, ddx)
			oL = acticeSourceObject.location
			oS = acticeSourceObject.scale
			#print ('Location',pd['u'], pd['v'], pd['w'], acticeSourceObject.location)
			#print ('Scale',dd['u'], dd['v'], dd['w'], acticeSourceObject.scale)
			#new_active.location = Vector((pdx, pdy, pdz))
			#new_active.scale = Vector((ddx, ddy, ddz))	
			# recalculate the new dimensions
			mino, maxo, f, addMin, addMax, mink, maxk, ddk, pdk = {}, {}, {}, {}, {}, {}, {}, {}, {}
			# f is the distance between to points in the Lattice (before the deform)
			mino['u'], maxo['u'], f['u'] = - (oL.x + 0.5) / oS.x, - (oL.x - 0.5) / oS.x, 1.0 / (l['u']-1) / oS.x
			mino['v'], maxo['v'], f['v'] = - (oL.y + 0.5) / oS.y, - (oL.y - 0.5) / oS.y, 1.0 / (l['v']-1) / oS.y
			mino['w'], maxo['w'], f['w'] = - (oL.z + 0.5) / oS.z, - (oL.z - 0.5) / oS.z, 1.0 / (l['w']-1) / oS.z
			for dir in dimA:
				addMin[dir] = max(0, math.ceil((mino[dir] - minv[dir] - 1e-5) / f[dir]))
				addMax[dir] = max(0, math.ceil((maxv[dir] - maxo[dir] - 1e-5) / f[dir]))
				#print (mino[dir], maxo[dir], minv[dir], maxv[dir], f[dir], addMin[dir], addMax[dir] )
				mink[dir] = mino[dir] - addMin[dir] * f[dir]
				maxk[dir] = maxo[dir] + addMax[dir] * f[dir]
				# you have to obey the steps done by the old Lattice...
				ddk[dir] = 1.0 / (maxk[dir] - mink[dir])
				pdk[dir] = - mink[dir] * ddk[dir] - 0.5
			for dir in dimA:
				saveData = {}
				cDim1 = dimAA[dir][0]
				cDim2 = dimAA[dir][1]
				# save the co_deforms of the Lattice before we change their dimension
				for j1 in range(l[cDim1]):
					for j2 in range(l[cDim2]):
						indElem = "%02i" % j1 + '.' + "%02i" % j2 
						elem = {}
						for i in range(l[dir]):
							index = factors[dir] * i + factors[cDim1] * j1 + factors[cDim2] * j2
							elem[i] = activeLattice.data.points[index].co_deform
						saveData[indElem] = elem
				#print (saveData)
				nln = l[dir] + addMin[dir] + addMax[dir]
				#print (addMin[dir], addMax[dir], nln, l[dir])
				if l[dir] < nln:
					if dir == 'u':
						activeLattice.data.points_u = nln
					if dir == 'v':
						activeLattice.data.points_v = nln
					if dir == 'w':
						activeLattice.data.points_w = nln
					l[dir] = nln
					factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
					for j1 in range(l[cDim1]):
						for j2 in range(l[cDim2]):
							indElem = "%02i" % j1 + '.' + "%02i" % j2 
							for i in range(l[dir]):
								index = factors[dir] * i + factors[cDim1] * j1 + factors[cDim2] * j2
								if i < addMin[dir]:
									v1 = saveData[indElem][0]
									v2 = saveData[indElem][1]
									vp = (v1 - v2) * (addMin[dir] - i) + v1
									activeLattice.data.points[index].co_deform = vp
									#print ('pred ', indElem, i)
								elif nln - addMax[dir] <= i:
									last1 = nln - addMax[dir] - addMin[dir] - 1
									last2 = nln - addMax[dir] - addMin[dir]  - 2
									v1 = saveData[indElem][last1]
									v2 = saveData[indElem][last2]
									#print ('past ', indElem, i, i - nln + addMax[dir] + 1)
									vp = (v1 - v2) * (i - nln + addMax[dir] + 1) + v1
									activeLattice.data.points[index].co_deform = vp
								else:
									i_old = i - addMin[dir]
									#print ('old  ', indElem, i, i_old)
									activeLattice.data.points[index].co_deform = saveData[indElem][i_old]
		
			acticeSourceObject.location = Vector((pdk['u'], pdk['v'], pdk['w']))
			acticeSourceObject.scale = Vector((ddk['u'], ddk['v'], ddk['w']))
		return {'FINISHED'}
		
class LatticeUnBind(bpy.types.Operator):
	'''UnBind a Lattice'''
	bl_idname = 'lattice.unbind'
	bl_label = 'LatticeUnbind'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'LATTICE')

	def execute(self, context):
		activeLattice = bpy.context.active_object
		acticeSourceObject = None
		modifierLattice = None
		lattice = None
		# find the right base-object
		for item in bpy.context.scene.objects:
			if item.type == 'MESH':
				#print (item.name, item.type)
				for modifier in item.modifiers:
					if modifier.type == 'LATTICE' and modifier.object == activeLattice:
						acticeSourceObject = item
						modifierLattice = modifier
						lattice = modifier.object
		if acticeSourceObject!=None:
			# now do a lot of operations
			#print(acticeSourceObject, modifierLattice, modifierLattice.name)
			bpy.ops.object.select_all(action='DESELECT')
			acticeSourceObject.select = True
			bpy.context.scene.objects.active = acticeSourceObject
			bpy.ops.object.make_single_user(object=True, obdata=True)
			i = 0
			#print(acticeSourceObject.modifiers.values())
			#print(acticeSourceObject.modifiers.items())
			while i < len(acticeSourceObject.modifiers):
				#print (i,acticeSourceObject.modifiers[i].name, acticeSourceObject.modifiers[i].type, acticeSourceObject.modifiers[i].show_viewport)
				if acticeSourceObject.modifiers[i].name == modifierLattice.name and acticeSourceObject.modifiers[i].type == 'LATTICE':
					i = len(acticeSourceObject.modifiers)
				else:
					if acticeSourceObject.modifiers[i].show_viewport:
						bpy.ops.object.modifier_apply(apply_as='DATA', modifier=acticeSourceObject.modifiers[i].name)
					else:
						i += 1
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifierLattice.name)
			acticeSourceObject.location += lattice.location
			#print(modifier.name, modifier.type, modifier.object == activeLattice)
			constraint = None
			for item in acticeSourceObject.constraints:
				#print (item.type, item.target, item.target==lattice)
				if item.type=='COPY_LOCATION' and item.target==lattice:
					constraint = item
			if constraint!=None:
				acticeSourceObject.constraints.remove(constraint)
			bpy.ops.object.select_all(action='DESELECT')
			lattice.select = True
			bpy.context.scene.objects.active = lattice
			bpy.ops.object.delete()
			acticeSourceObject.select = True
			bpy.context.scene.objects.active = acticeSourceObject

		return {'FINISHED'}

class LatticeLinearAdd(bpy.types.Operator):
	'''test an algorithm for Lattices a'''
	bl_idname = 'lattice.latticelinearadd'
	bl_label = 'LatticeLinearAdd'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'LATTICE')
		
	def execute(self, context):
		activeLattice = bpy.context.active_object
		lattice_dir = context.scene.lattice_dir
		addSamples = context.scene.lattice_add_samples
		addSamplesMode = context.scene.lattice_add_samplesmode
		#logging.info('execute start')
		l = {}
		l['u'] = activeLattice.data.points_u
		l['v'] = activeLattice.data.points_v
		l['w'] = activeLattice.data.points_w
		if l[lattice_dir] < 3:
			return {'FINISHED'}
		dimA = ['u','v','w']
		dimAA = {'u':['v','w',0],'v':['u','w',1],'w':['u','v',2]}
		# factors for multiplying
		factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
		# first find the selected layers
		layers = []
		counterDim1 = dimAA[lattice_dir][0]
		counterDim2 = dimAA[lattice_dir][1]
		# make a list of all possible distributions
		distributes = allDistributions(addSamples,l[lattice_dir]-1)
		distributesList = {}
		for distribute in distributes:
			#print(distribute)
			distributesList[','.join([str(k) for k in distribute])] = distribute
		#print('++++++++')
		erg = {}
		originalPoints = {}
		#for i in range(len(activeLattice.data.points)):
		#	#print("%03i" % i, activeLattice.data.points[i].co, activeLattice.data.points[i].co_deform)
		for j1 in range(l[counterDim1]):
			originalPoints[j1] = {}
			for j2 in range(l[counterDim2]):
				originalPoints[j1][j2] = {'v':{}}
				for i in range(l[lattice_dir]):
					# save the Original deform
					index = factors[lattice_dir] * i + factors[counterDim1] * j1 + factors[counterDim2] * j2
					#logging.info(counterDim1 + ' ' + counterDim2 + ' ' + lattice_dir + ' ' + str(j1) + ' ' + str(j2) + ' ' + str(i) + ' : ' + str(index))
					#data[counterDim1], data[counterDim2], data[lattice_dir] = j1, j2, i
					#data[index] = activeLattice.data.points[index].co_deform
					originalPoints[j1][j2]['v'][i] = activeLattice.data.points[index].co_deform.copy()
				bestCombination, bestValue = '', 999999.9
				for distributeName, distributeElem in distributesList.items():
					minSpace, maxSpace = 99999.9, -1.0 
					for i in range(l[lattice_dir]-1):
						index = factors[lattice_dir] * i + factors[counterDim1] * j1 + factors[counterDim2] * j2
						indexp = factors[lattice_dir] * (i+1) + factors[counterDim1] * j1 + factors[counterDim2] * j2
						ll = (activeLattice.data.points[indexp].co_deform - activeLattice.data.points[index].co_deform).length
						minSpace = min(minSpace, ll / (distributeElem[i] + 1))
						maxSpace = max(maxSpace, ll / (distributeElem[i] + 1))
					if distributeName not in erg:
						erg[distributeName] = []
					erg[distributeName].append(maxSpace - minSpace)
					if maxSpace - minSpace < bestValue:
						bestValue = maxSpace - minSpace
						bestCombination = distributeName
				originalPoints[j1][j2]['comb'] = bestCombination
				# evaluate best Combination
				#originalPoints[j1][j2]['bestCombination']
		bestCombination, bestValue = '', 999999.9
		for comb,values in erg.items():
			if max(values) < bestValue:
				bestValue = max(values)
				bestCombination = comb
		#print (erg)
		#print (bestValue, bestCombination)
		comb = bestCombination.split(',')
		if lattice_dir == 'u':
			activeLattice.data.points_u += addSamples
			l['u']  += addSamples
		if lattice_dir == 'v':
			activeLattice.data.points_v += addSamples
			l['v']  += addSamples
		if lattice_dir == 'w':
			activeLattice.data.points_w += addSamples
			l['w']  += addSamples
		factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
		for j1 in range(l[counterDim1]):
			for j2 in range(l[counterDim2]):
				#print (j1,j2, originalPoints[j1][j2])
				if addSamplesMode:
					comb = originalPoints[j1][j2]['comb'].split(',')
				m = 0
				for ji,k in enumerate(comb):
					data_start = originalPoints[j1][j2]['v'][ji]
					data_stop = originalPoints[j1][j2]['v'][ji + 1]
					kk = int(k) + 1
					dx,dy,dz = (data_stop.x - data_start.x) / kk, (data_stop.y - data_start.y) / kk, (data_stop.z - data_start.z) / kk
					for jj in range(kk + 1):
						index = factors[lattice_dir] * m + factors[counterDim1] * j1 + factors[counterDim2] * j2
						activeLattice.data.points[index].co_deform.x = data_start.x + jj * dx
						activeLattice.data.points[index].co_deform.y = data_start.y + jj * dy
						activeLattice.data.points[index].co_deform.z = data_start.z + jj * dz
						#print (m,k,ji,jj, data_start.z, data_stop.z, data_start.z + jj * dz)
						m += 1
					m -= 1
		return {'FINISHED'}
		
def allDistributions(points, samples):
	erg = []
	if samples < 2:
		erg.append([points])
	else:
		if points == 0:
			erg.append([0 for i in range(samples)])
		else:
			for i in range(0,points+1):
				rest = points - i
				suberg = allDistributions(rest, samples - 1)
				for k in suberg:
					erg.append([i] + k)
	return erg
		
class LatticeCubicReorder(bpy.types.Operator):
	'''test an algorithm for Lattices'''
	bl_idname = 'lattice.latticecubicreorder'
	bl_label = 'LatticeTestReorder'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if not obj or obj.type != 'LATTICE':
			return False
		lattice_dir = context.scene.lattice_dir
		lu = obj.data.points_u
		lv = obj.data.points_v
		lw = obj.data.points_w
		if lattice_dir == 'u' and lu < 4:
			return False
		if lattice_dir == 'v' and lv < 4:
			return False
		if lattice_dir == 'w' and lw < 4:
			return False
		return True
		
	def execute(self, context):
		activeLattice = bpy.context.active_object
		lattice_dir = context.scene.lattice_dir
		samples = context.scene.lattice_reorder_samples
		samplesMode = context.scene.lattice_reorder_samplesmode
		#logging.info('execute start')
		#print ('execute start')
		l = {}
		l['u'] = activeLattice.data.points_u
		l['v'] = activeLattice.data.points_v
		l['w'] = activeLattice.data.points_w
		if l[lattice_dir] < 4:
			return {'FINISHED'}
		dimA = ['u','v','w']
		dimAA = {'u':['v','w',0],'v':['u','w',1],'w':['u','v',2]}
		# factors for multiplying
		factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
		# first find the selected layers
		layers = []
		counterDim1 = dimAA[lattice_dir][0]
		counterDim2 = dimAA[lattice_dir][1]
		if samplesMode:
			splines = [[[] for i in range(l[counterDim1])] for j in range(l[counterDim2])]
			#print(splines)
			for j1 in range(l[counterDim1]):
				for j2 in range(l[counterDim2]):
					for i in range(l[lattice_dir]):
						index = factors[lattice_dir] * i + factors[counterDim1] * j1 + factors[counterDim2] * j2
						#print (i, activeLattice.data.points[i].co)
						splines[j2][j1].append(activeLattice.data.points[index].co_deform)
			if lattice_dir == 'u':
				activeLattice.data.points_u = samples
			if lattice_dir == 'v':
				activeLattice.data.points_v = samples
			if lattice_dir == 'w':
				activeLattice.data.points_w = samples
			l[lattice_dir] = samples
			factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
			for j1 in range(l[counterDim1]):
				for j2 in range(l[counterDim2]):
					nv = spline (splines[j2][j1], samples, 1, 1)
					ran = range(1,samples - 1)
					for i in ran:
						index = factors[lattice_dir] * i + factors[counterDim1] * j1 + factors[counterDim2] * j2
						#print (i,iw,iv,iu)
						activeLattice.data.points[index].co_deform.x = nv[0][i]
						activeLattice.data.points[index].co_deform.y = nv[1][i]
						activeLattice.data.points[index].co_deform.z = nv[2][i]
		else:
			for i in range(l[lattice_dir]):
				layerData = {}
				layer = {}
				for j1 in range(l[counterDim1]):
					for j2 in range(l[counterDim2]):
						index = factors[lattice_dir] * i + factors[counterDim1] * j1 + factors[counterDim2] * j2
						data = {'index':index}
						data['co'] = activeLattice.data.points[index].co.copy()
						data['co'][dimAA[lattice_dir][2]] = 0.0
						data['co_deform'] = activeLattice.data.points[index].co_deform.copy()
						layer[index] = data
				parameter = calc_deform(layer)
				#logging.info(str(layer))
				#logging.info(str(parameter))
				layerData['layer'] = layer
				layerData['parameter'] = parameter
				layers.append(layerData)
			splineData = []
			for i in range(len(layers)):
				co = [0,0,0,0,0,0,0]
				par = layers[i]['parameter']
				co[0],co[1],co[2],co[3],co[4],co[5],co[6] = par[4],par[5],par[6], par[1],par[2],par[3],par[7]
				if 0 < i:
					co[3] = closestAngle(co[3], splineData[i-1][3])
					co[4] = closestAngle(co[4], splineData[i-1][4])
					co[5] = closestAngle(co[5], splineData[i-1][5])
				splineData.append(co)
			#logging.info('splineData ' + str(splineData))
			#spline (splineData, len(splineData), 1, 1)
			#samples = len(layers)
			
			data = spline (splineData, samples, 1, 1)
			if lattice_dir == 'u':
				activeLattice.data.points_u = samples
			if lattice_dir == 'v':
				activeLattice.data.points_v = samples
			if lattice_dir == 'w':
				activeLattice.data.points_w = samples
			l[lattice_dir] = samples
			factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
			#logging.info('data erg:\n' + str(data))
			# todo, abgleich mit activeLattice.data.points_u,...
			for i in range(l[lattice_dir]):
				for j1 in range(l[counterDim1]):
					for j2 in range(l[counterDim2]):
						index = factors[lattice_dir] * i + factors[counterDim1] * j1 + factors[counterDim2] * j2
						co = activeLattice.data.points[index].co.copy()
						co[dimAA[lattice_dir][2]] = 0.0
						v = {1: co[0], 2: co[1], 3: co[2]}
						w = {1:data[3][i], 2:data[4][i], 3:data[5][i], 4:data[0][i], 5:data[1][i], 6:data[2][i], 7:data[6][i]}
						vp, vr = calc_deform_step(w,v)
						activeLattice.data.points[index].co_deform = Vector((vp[1], vp[2], vp[3]))
		return {'FINISHED'}

class LatticeForgePlanar(bpy.types.Operator):
	'''forges all layer to be planar'''
	bl_idname = 'lattice.latticeforgeplanar'
	bl_label = 'LatticeForgePlanar'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'LATTICE')

	def execute(self, context):
		#global logging 
		#logging.info("\n************************* Start")
		activeLattice = bpy.context.active_object
		lattice_forgedir = context.scene.lattice_forgedir
		dimA = ['u','v','w']
		dimAA = {'u':['v','w',0],'v':['u','w',1],'w':['u','v',2]}
		l = {}
		l['u'] = activeLattice.data.points_u
		l['v'] = activeLattice.data.points_v
		l['w'] = activeLattice.data.points_w
		# factors for multiplying
		factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
		layers = []
		for i in range(l[lattice_forgedir]):
			layer = []
			j1Target = dimAA[lattice_forgedir][0]
			j2Target = dimAA[lattice_forgedir][1]
			for j1 in range(l[j1Target]):
				for j2 in range(l[j2Target]):
					index = factors[lattice_forgedir] * i + factors[j1Target] * j1 + factors[j2Target] * j2
					layer.append({'index':index})
			#logging.info (str(layer))
			layers.append({'layer': layer, 'index': i})
		estimate = [1.0 for i in range(3 * len(layers))]
		# for controlling
		#logging.info ('define(V(v),matrix([v[1],v[2],v[3]]));')
		#logging.info ('define(P(p),matrix([p[1],p[2],p[3]]));')
		#logging.info ('define(VP(v,p), V(v).P(p));')
		#logging.info ('define(VV(v), sqrt(V(v).V(v)));')
		#logging.info ('define(h(v,p), VP(v,p) / VV(v) - VV(v));')
		# derives to the different coordinates
		#logging.info ('define(h_x(v,p), diff(h(v,p),v[1]));')
		#logging.info ('define(h_y(v,p), diff(h(v,p),v[2]));')
		#logging.info ('define(h_z(v,p), diff(h(v,p),v[3]));')
		w = 1000
		errorHist = []
		while 0 < w:
			#logging.info ('***** ' + str(w) + ' *****')
			#print('***** ' + str(w))
			w -= 1
			m = matrix()
			t = []
			mi = 0
			for i in range(len(layers)):
				#logging.info ('** Layer ' + str(i))
				v_x , v_y , v_z = estimate[3*i] , estimate[3*i + 1] , estimate[3*i + 2]
				log_v = '[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + ']'
				#logging.info ('v[' + str(i) + ']:[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + ']' )
				for poiElem in layers[i]['layer']:
					poi = poiElem['index']
					co = activeLattice.data.points[poi].co_deform.copy()
					log_p = '[' + str(co.x) + ',' + str(co.y) + ',' + str(co.z) + ']'
					#logging.info ('p:[' + str(co.x) + ',' + str(co.y) + ',' + str(co.z) + ']' )
					dot_prod = v_x * co.x + v_y  * co.y + v_z * co.z
					vv = v_x * v_x + v_y  * v_y + v_z * v_z
					v = sqrt(vv)
					# targetValue
					h = dot_prod / v - v
					#logging.info ('h(' + log_v + ',' + log_p + ');')
					#logging.info ('=>' + str(h))
					# derivatives
					dx = co.x / v - v_x * (dot_prod / (vv * v) + 1 / v)
					dy = co.y / v - v_y * (dot_prod / (vv * v) + 1 / v)
					dz = co.z / v - v_z * (dot_prod / (vv * v) + 1 / v)
					#logging.info ('h_x(' + log_v + ',' + log_p + ');')
					#logging.info ('h_y(' + log_v + ',' + log_p + ');')
					#logging.info ('h_z(' + log_v + ',' + log_p + ');')
					#logging.info ('=>' + str(dx) + ',' + str(dy) + ',' + str(dz))
					#print ('poi' , i , poi , co, dot_prod, v, dx, dy, dz)
					#print (dx, dy, dz)
					m.set(mi,3*i  ,dx)
					m.set(mi,3*i+1,dy)
					m.set(mi,3*i+2,dz)
					t.append(h)
					#t.append(dist[3])
					mi += 1
			#logging.info ('')
			#logging.info ('diff %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f', dist_diffwx, dist_diffwy, dist_diffwz, dist_difftx, dist_diffty, dist_difftz, dist_diffs )
			#meanErrorRaw = 0.0
			#if 0 < ii:
			#logging.info (m.writeWMaxima('d'))
			#print ('m')
			#m.write()
			#print(m.writeWMaxima('d'))
			ma = m.t_copy().mul_matrix(m)
			#logging.info ('dd:transpose(d).d;')
			#logging.info (ma.writeWMaxima('=>'))
			#logging.info ('')
			vb = m.t_copy().mul_vektor(t)
			#logging.info ('t:matrix(' + str(t) + ');')
			#logging.info ('vb:transpose(d).t');
			#logging.info ('=>:' + str(vb))
			#print ('vb', vb)
			
			mt = ma.copy().appendCol(vb)
			ee = ma.cholesky(vb)
			#logging.info (mt.writeWMaxima('mt'))
			#logging.info ('linsolve(maplist(first,mt.[w1x,w1y,w1z,w2x,w2y,w2z,-1]),[w1x,w1y,w1z,w2x,w2y,w2z]);')
			#logging.info ('ee: ' + str(ee))
			#logging.info ('estimate direction: ' + str(ee))
			error = 0.0
			for i,vv in enumerate(estimate):
				error += ee[i]*ee[i]
				estimate[i] += 0.5*ee[i]
			if error < 1e-7:
				w = 0
			errorHist.append(error)
			#logging.info ('estimate' + str(estimate))
			
		#logging.info('')
		#logging.info('ErrorHistorie: ' + str(errorHist))
		
		# make the results
		for i in range(len(layers)):
			#logging.info ('** Layer Result ' + str(i))
			v_x , v_y , v_z = estimate[3*i] , estimate[3*i + 1] , estimate[3*i + 2]
			log_v = '[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + ']'
			#logging.info ('v[' + str(i) + ']:[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + ']' )
			for poiElem in layers[i]['layer']:
				poi = poiElem['index']
				co = activeLattice.data.points[poi].co_deform.copy()
				log_p = '[' + str(co.x) + ',' + str(co.y) + ',' + str(co.z) + ']'
				#logging.info ('p:[' + str(co.x) + ',' + str(co.y) + ',' + str(co.z) + ']' )
				dot_prod = v_x * co.x + v_y  * co.y + v_z * co.z
				vv = v_x * v_x + v_y  * v_y + v_z * v_z
				v = sqrt(vv)
				# targetValue
				h = dot_prod / v - v
				#logging.info ('h: ' + str(h) )
				co.x, co.y, co.z = co.x - h * v_x / v,  co.y - h * v_y / v, co.z - h * v_z / v
				activeLattice.data.points[poi].co_deform = co
				
		logging.shutdown()
		return {'FINISHED'}

class LatticeForgeMultiPlanar(bpy.types.Operator):
	'''forges all layer to be planar in the same direction'''
	bl_idname = 'lattice.latticeforgemultiplanar'
	bl_label = 'LatticeForgeMultiPlanar'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'LATTICE')

	def execute(self, context):
		#global logging
		#logging.info("\n************************* Start")
		activeLattice = bpy.context.active_object
		lattice_forgedir = context.scene.lattice_forgedir
		dimA = ['u','v','w']
		dimAA = {'u':['v','w',0],'v':['u','w',1],'w':['u','v',2]}
		l = {}
		l['u'] = activeLattice.data.points_u
		l['v'] = activeLattice.data.points_v
		l['w'] = activeLattice.data.points_w
		# factors for multiplying
		factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
		layers = []
		for i in range(l[lattice_forgedir]):
			layer = []
			j1Target = dimAA[lattice_forgedir][0]
			j2Target = dimAA[lattice_forgedir][1]
			for j1 in range(l[j1Target]):
				for j2 in range(l[j2Target]):
					index = factors[lattice_forgedir] * i + factors[j1Target] * j1 + factors[j2Target] * j2
					layer.append({'index':index})
			#logging.info (str(layer))
			layers.append({'layer': layer, 'index': i})
		estimate = [1.0/113 for i in range(2 + len(layers))]
		# *** for controlling
		#logging.info ('define(V(v,b),matrix([b*v[1],b*v[2],b*v[3]]));')
		#logging.info ('define(P(p),matrix([p[1],p[2],p[3]]));')
		#logging.info ('define(VP(v,b,p), V(v,b).P(p));')
		#logging.info ('define(VV(v,b), sqrt(V(v,b).V(v,b)));')
		#logging.info ('define(h(v,b,p), VP(v,b,p) / VV(v,b) - VV(v,b));')
		# *** derives to the different coordinates
		#logging.info ('define(h_x(v,b,p), diff(h(v,b,p),v[1]));')
		#logging.info ('define(h_y(v,b,p), diff(h(v,b,p),v[2]));')
		#logging.info ('define(h_z(v,b,p), diff(h(v,b,p),v[3]));')
		#logging.info ('define(h_b(v,b,p), diff(h(v,b,p),b));')
		w = 1000
		errorHist = []
		maxLayerConsidered = 1
		while 0 < w:
			#logging.info ('***** ' + str(w) + ' *****')
			w -= 1
			m = matrix()
			t = []
			mi = 0
			v_x , v_y , v_z = estimate[0] , estimate[1] , estimate[2]
			for i in range(maxLayerConsidered):
				#logging.info ('** Layer ' + str(i))
				b = 1.0
				if 0 < i:
					b = estimate[2 + i]
				log_v = '[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + '],' + str(b)
				#logging.info ('v[' + str(i) + ']:[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + ']' )
				for poiElem in layers[i]['layer']:
					poi = poiElem['index']
					co = activeLattice.data.points[poi].co_deform.copy()
					log_p = '[' + str(co.x) + ',' + str(co.y) + ',' + str(co.z) + ']'
					
					dot_prod = (v_x * co.x + v_y  * co.y + v_z * co.z) * b
					vvr = (v_x * v_x + v_y  * v_y + v_z * v_z)
					vr = sqrt(vvr)
					vv = vvr * b * b
					v = sqrt(vv)
					vvv = v * vv
					# targetValue
					h = 0.0
					dx, dy, dz = 0.0, 0.0, 0.0
					#logging.info ('v: ' + str(v) )
					#logging.info ('h(' + log_v + ',' + log_p + ');')
					if 1e-9 < abs(v):
						h = dot_prod / v - v
						#logging.info ('=>' + str(h))
						dx = (co.x * b - v_x * b * b) / v - v_x * b * b * dot_prod / vvv
						dy = (co.y * b - v_y * b * b) / v - v_y * b * b * dot_prod / vvv
						dz = (co.z * b - v_z * b * b) / v - v_z * b * b * dot_prod / vvv
					db = -vr
					#logging.info ('h_x(' + log_v + ',' + log_p + ');')
					#logging.info ('h_y(' + log_v + ',' + log_p + ');')
					#logging.info ('h_z(' + log_v + ',' + log_p + ');')
					#logging.info ('h_b(' + log_v + ',' + log_p + ');')
					#logging.info ('=>' + str(dx) + ',' + str(dy) + ',' + str(dz) + ',' + str(db))
					m.set(mi,0,dx)
					m.set(mi,1,dy)
					m.set(mi,2,dz)
					if 0 < i:
						m.set(mi,i+2,db)
					t.append(h)
					#t.append(dist[3])
					mi += 1
			#logging.info (m.writeWMaxima('d'))
			ma = m.t_copy().mul_matrix(m)
			#logging.info ('dd:transpose(d).d;')
			#logging.info (ma.writeWMaxima('=>'))
			#logging.info ('')
			vb = m.t_copy().mul_vektor(t)
			#logging.info ('t:matrix(' + str(t) + ');')
			#logging.info ('vb:transpose(d).t');
			#logging.info ('=>:' + str(vb))
			mt = ma.copy().appendCol(vb)
			ee = ma.cholesky(vb)
			#logging.info (mt.writeWMaxima('mt'))
			#logging.info ('linsolve(maplist(first,mt.[wx,wy,wz,a1,a2,-1]),[wx,wy,wz,a1,a2]);')
			#logging.info ('ee: ' + str(ee))
			#logging.info ('estimate direction: ' + str(ee))
			error = 0.0
			for i,vv in enumerate(estimate):
				if i < 2 + maxLayerConsidered:
					#logging.info ('xx: ' + str(i) + ' ' + str(ee[i]))
					error += ee[i]*ee[i]
					#if 1.0 < ee[i]:
					#	ee[i] = 1.0
					#if ee[i] < -1.0:
					#	ee[i] = -1.0
					estimate[i] += 0.25 * ee[i]
			if error < 1e-7:
				if maxLayerConsidered < len(layers):
					maxLayerConsidered += 1
				else:
					w = 0
			errorHist.append(error)
			#logging.info ('LayerConsidered: ' + str(maxLayerConsidered) + ', error: ' + str(error))
			#logging.info ('estimate' + str(estimate))
			
		#logging.info('')
		#logging.info('ErrorHistorie: ' + str(errorHist))
		#logging.info ('estimate' + str(estimate))
			
		# make the results
		v_x , v_y , v_z = estimate[0] , estimate[1] , estimate[2]
		for i in range(len(layers)):
			#logging.info ('** Layer Result ' + str(i))
			b = 1.0
			if 0 < i:
				b = estimate[2 + i]
			#log_v = '[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + ']'
			#logging.info ('v[' + str(i) + ']:[' + str(v_x) + ',' + str(v_y) + ',' + str(v_z) + ']' )
			for poiElem in layers[i]['layer']:
				poi = poiElem['index']
				co = activeLattice.data.points[poi].co_deform.copy()
				#log_p = '[' + str(co.x) + ',' + str(co.y) + ',' + str(co.z) + ']'
				#logging.info ('p:[' + str(co.x) + ',' + str(co.y) + ',' + str(co.z) + ']' )
				dot_prod = (v_x * co.x + v_y  * co.y + v_z * co.z) * b
				vvr = (v_x * v_x + v_y  * v_y + v_z * v_z)
				vv = vvr * b * b
				v = sqrt(vv)
				# targetValue
				if 1e-7 < v:
					h = dot_prod / v - v
					#logging.info ('h: ' + str(h) )
					co.x, co.y, co.z = co.x - b * h * v_x / v,  co.y - b * h * v_y / v, co.z - b * h * v_z / v
					#co.x, co.y, co.z = co.x - h * v_x / v,  co.y - h * v_y / v, co.z - h * v_z / v
					activeLattice.data.points[poi].co_deform = co
				
		return {'FINISHED'}
		
def closestAngle(original, bias):
	#ori = original
	while pi < original - bias:
		original -= 2*pi
	while pi < bias - original:
		original += 2*pi
	#logging.info ('closestAngle ' + str(ori) + ',' + str(bias) + ' => ' + str(original))
	return original
		
class LatticeTest(bpy.types.Operator):
	'''test an algorithm for Lattices'''
	bl_idname = 'lattice.latticetest'
	bl_label = 'LatticeTest'
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'LATTICE')

	def execute(self, context):
		#logging.info("\n************************* Start")
		dimA = ['u','v','w']
		dimAA = {'u':['v','w',0],'v':['u','w',1],'w':['u','v',2]}
		activeLattice = bpy.context.active_object
		l = {}
		l['u'] = activeLattice.data.points_u
		l['v'] = activeLattice.data.points_v
		l['w'] = activeLattice.data.points_w
		# factors for multiplying
		factors = {'u': 1, 'v':l['u'], 'w': l['u']*l['v']}
		# first find the selected layers
		selected = [i for i in range(len(activeLattice.data.points)) if activeLattice.data.points[i].select]
		sel = {'u':{}, 'v':{}, 'w':{}}
		index = {}
		# sort all selected verts in the lattice to it's corresponding u,v,w-layer
		for i in selected:
			index['u'] = i % l['u']
			index['v'] = (i // l['u']) % l['v']
			index['w'] = (i // l['u'] // l['v']) % l['w']
			for di in dimA:
				if index[di] not in sel[di]:
					sel[di][index[di]] = []
				sel[di][index[di]].append(i)
		# select all layer with full points
		erg = {'u':{}, 'v':{}, 'w':{}}
		# fail filters out those layers, where not all verts per layer are selected
		fail = {'u':0, 'v':0, 'w':0}
		for dii in dimA:
			for di in range(l[dii]):
				if di in sel[dii]:
					prod = l[dimAA[dii][0]] * l[dimAA[dii][1]]
					if len(sel[dii][di]) == prod:
						erg[dii][di] = sel[dii][di]
					elif 0 < len(sel[dii][di]):
						fail[dii] += 1
		for dii in dimA:
			if 0 < fail[dii]:
				erg[dii] = {}
		#print (erg)
		# todo, here a test that not all verts of the lattice are selected
		# maybe use the product of fails, it must be zero
		
		# calculate the parameters for the layers 
		for dii in dimA:
			if 0 < len(erg[dii]):
				layers = {}
				for i in range(l[dii]):
					layers[i] = {'layer':{}}
					for i1 in range(l[dimAA[dii][0]]):
						for i2 in range(l[dimAA[dii][1]]):
							index = i * factors[dii] + i1 * factors[dimAA[dii][0]] + i2 * factors[dimAA[dii][1]]
							layers[i]['layer'][index] = {}
					# translation, rotation and scale
					for j in layers[i]['layer'].keys():
						layers[i]['layer'][j]['co'] = activeLattice.data.points[j].co.copy()
						layers[i]['layer'][j]['co'][dimAA[dii][2]] = 0.0
						layers[i]['layer'][j]['co_deform'] = activeLattice.data.points[j].co_deform.copy()
					layers[i]['layer']['parameter'] = calc_deform(layers[i]['layer'])
					#logging.info ('values for ' + str(i) + ': ' + str(layers[i]['layer']['parameter']))
					#parameter = {'tx':0, 'ty':0, 'tz':0, 's':1, 'rx':0, 'ry':0, 'rz':0}
				#print (layers)
		return {'FINISHED'}
		
def calc_rotation_to_vector(wx,wy,wz):
	vx = sin(wx)*sin(wz)-cos(wx)*sin(wy)*cos(wz)-cos(wx)*sin(wz)-sin(wx)*sin(wy)*cos(wz)+cos(wy)*cos(wz)
	vy = cos(wx)*cos(wz)-sin(wx)*sin(wy)*sin(wz)-cos(wx)*sin(wy)*sin(wz)-sin(wx)*cos(wz)+cos(wy)*sin(wz)
	vz = sin(wy)+sin(wx)*cos(wy)+cos(wx)*cos(wy)
	return vx,vy,vz
	
def calc_vector_to_rotation(vx,vy,vz):
	dist = sqrt(vx*vx + vy*vy + vz*vz)
	if dist < 1-12:
		return 0.0, 0.0, 0.0
	vx /= dist 
	vy /= dist
	vz /= dist
	wx, wy, wz = 0.0, 0.0, 0.0
	
	vrx = sin(wx)*sin(wz)-cos(wx)*sin(wy)*cos(wz)-cos(wx)*sin(wz)-sin(wx)*sin(wy)*cos(wz)+cos(wy)*cos(wz)
	vry = cos(wx)*cos(wz)-sin(wx)*sin(wy)*sin(wz)-cos(wx)*sin(wy)*sin(wz)-sin(wx)*cos(wz)+cos(wy)*sin(wz)
	vrz = sin(wy)+sin(wx)*cos(wy)+cos(wx)*cos(wy)
	
	diffwx = {1: sin(wx)*sin(wz)-cos(wx)*sin(wy)*cos(wz) + cos(wx)*sin(wz)+sin(wx)*sin(wy)*cos(wz), \
		2: sin(wx)*sin(wy)*sin(wz)-cos(wx)*cos(wz) - cos(wx)*sin(wy)*sin(wz) - sin(wx)*cos(wz), \
		3: cos(wx)*cos(wy) - sin(wx)*cos(wy) }

	diffwy = {1: -sin(wy)*cos(wz) - sin(wx)*cos(wy)*cos(wz) - cos(wx)*cos(wy)*cos(wz), \
		2: -sin(wy)*sin(wz) - sin(wx)*cos(wy)*sin(wz) - cos(wx)*cos(wy)*sin(wz), \
		3: -sin(wx)*sin(wy) - cos(wx)*sin(wy) + cos(wy)}

	diffwz = {1: sin(wx)*sin(wy)*sin(wz)-cos(wx)*cos(wz) + cos(wx)*sin(wy)*sin(wz)+sin(wx)*cos(wz) - cos(wy)*sin(wz), \
		2: sin(wx)*sin(wz)-cos(wx)*sin(wy)*cos(wz) - cos(wx)*sin(wz) + sin(wx)*sin(wy)*cos(wz) + cos(wy)*cos(wz), \
		3: 0}
	
	# TODO: alot

def calc_deform_step(w,v):
	vp, vr = {}, {}
	vr[1] = v[3]*(sin(w[1])*sin(w[3])-cos(w[1])*sin(w[2])*cos(w[3]))+v[2]*(-cos(w[1])*sin(w[3])-sin(w[1])*sin(w[2])*cos(w[3]))+v[1]*cos(w[2])*cos(w[3])
	vr[2] = v[2]*(cos(w[1])*cos(w[3])-sin(w[1])*sin(w[2])*sin(w[3]))+v[3]*(-cos(w[1])*sin(w[2])*sin(w[3])-sin(w[1])*cos(w[3]))+v[1]*cos(w[2])*sin(w[3])
	vr[3] = v[1]*sin(w[2])+v[2]*sin(w[1])*cos(w[2])+v[3]*cos(w[1])*cos(w[2])
	# after rotation multiply with scale and add translation
	vp[1] = w[4] + vr[1]*w[7]
	vp[2] = w[5] + vr[2]*w[7]
	vp[3] = w[6] + vr[3]*w[7]
	return vp, vr
	
def calc_deform(data, mode=0):
	# the parameters are 1-3 = rotation, 4-6 = translation, 7 = scale
	# mode is for future expansions, when a there is more than just a scalable plane (cylinders, ellipsoids)
	# data are an arbitrary amount of points (minimum should be 3, but the estimates are getting better with a growing amount of points)
	#logging.info ('************ new approximation')
	w = {1:0.0, 2:0.0, 3:0.0, 4:0.0, 5:0.0, 6:0.0, 7:1.0}
	#logging.info ('data:\n' + str(data))
	maxCount = 50
	while 0 < maxCount:
		#logging.info ('\n***** new step: ' + str(maxCount))
		maxCount -= 1
		m = matrix()
		t = []
		v, p, ii = {}, {}, 0
		#logging.info ('w: ' + str(w))
		for i,vv in enumerate(data.keys()):
			v[1], v[2], v[3] = data[vv]['co'].x, data[vv]['co'].y, data[vv]['co'].z
			p[1], p[2], p[3] = data[vv]['co_deform'].x, data[vv]['co_deform'].y, data[vv]['co_deform'].z
			#logging.info ('sample point ' + str(i) + '\n- Blender vert index: ' + str(vv) + '\n- co' + str(v) + '\n- co-deform' + str(p))
			vp = {}
			vr = {}
			# Rotationmatrix multiplied with targetvector (this is vector one we do refer to)
			# vr is used for the derivative to the scale
			# after rotation multiply with scale and add translation
			#logging.info ('target values: ' + str(vp))
			vp, vr = calc_deform_step(w,v)
			
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

			# derivative of trajecting point
			#logging.info ('t ' + str(v))
			#logging.info ('p ' + str(p))
			#logging.info ('target %8.3f', target)
			
			m.set(ii,0,Mp_diffwx[1])
			m.set(ii,1,Mp_diffwy[1])
			m.set(ii,2,Mp_diffwz[1])
			m.set(ii,3,Mp_difftx[1])
			m.set(ii,4,Mp_diffty[1])
			m.set(ii,5,Mp_difftz[1])
			m.set(ii,6,Mp_diffs[1])
			t.append(dist[1])
			ii += 1
			m.set(ii,0,Mp_diffwx[2])
			m.set(ii,1,Mp_diffwy[2])
			m.set(ii,2,Mp_diffwz[2])
			m.set(ii,3,Mp_difftx[2])
			m.set(ii,4,Mp_diffty[2])
			m.set(ii,5,Mp_difftz[2])
			m.set(ii,6,Mp_diffs[2])
			t.append(dist[2])
			ii += 1
			m.set(ii,0,Mp_diffwx[3])
			m.set(ii,1,Mp_diffwy[3])
			m.set(ii,2,Mp_diffwz[3])
			m.set(ii,3,Mp_difftx[3])
			m.set(ii,4,Mp_diffty[3])
			m.set(ii,5,Mp_difftz[3])
			m.set(ii,6,Mp_diffs[3])
			t.append(dist[3])
			ii += 1
			#logging.info ('diff %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f', dist_diffwx, dist_diffwy, dist_diffwz, dist_difftx, dist_diffty, dist_difftz, dist_diffs )
		meanErrorRaw = 0.0
		if 0 < ii:
			#logging.info (m.writeWMaxima('d'))
			#print ('m')
			#m.write()
			ma = m.t_copy().mul_matrix(m)
			#logging.info (ma.writeWMaxima('dd'))
			#logging.info ('ma:transpose(d).d;')
			#print ('ma')
			#ma.write()
			#print ('t', t)
			vb = m.t_copy().mul_vektor(t)
			#logging.info ('t:matrix(' + str(t) + ');')
			#logging.info ('transpose(d).t');
			#logging.info ('vb:\n' + str(vb))
			#print ('vb', vb)
			mt = ma.copy().appendCol(vb)
			ee = ma.cholesky(vb)
			#logging.info (mt.writeWMaxima('mt'))
			#logging.info ('linsolve(maplist(first,mt.[wx,wy,wz,tx,ty,tz,s,-1]),[wx,wy,wz,tx,ty,tz,s]);')
			#logging.info ('ee: ' + str(ee))
			#print ('ee',ee)
			maxmov = 0.5
			meanErrorRaw = ee[0]*ee[0] + ee[1]*ee[1] + ee[2]*ee[2] + ee[3]*ee[3] + ee[4]*ee[4] + ee[5]*ee[5] + ee[6]*ee[6]
			# the rotation-angles should move slow, because the sometimes just seems erratic
			for i in range(3):
				if ee[i] < -maxmov:
					ee[i] = -maxmov
				if ee[i] > maxmov:
					ee[i] = maxmov
			meanError = ee[0]*ee[0] + ee[1]*ee[1] + ee[2]*ee[2] + ee[3]*ee[3] + ee[4]*ee[4] + ee[5]*ee[5] + ee[6]*ee[6]
			#print ('ee maxmov',ee)
			w = {1: w[1] + ee[0] , 2: w[2] + ee[1] , 3: w[3] + ee[2], 4: w[4] + ee[3] , 5: w[5] + ee[4], 6: w[6] + ee[5], 7: w[7] + ee[6]}
			#logging.info ('w',maxCount, "%8.3f" % w[1],"%8.3f" % w[2],"%8.3f" % w[3],"%8.3f" % w[4],"%8.3f" % w[5],"%8.3f" % w[6],"%8.3f" % w[7],"%8.3f" % meanErrorRaw)
			if meanError < 1e-9:
				maxCount = min(1,maxCount)
		#print ('final', final)
		#for e in erg:
		#	#print (e['h'])
	
	return w

		
class LatticeUnTorsion(bpy.types.Operator):
	'''UnTorsion a Lattice'''
	bl_idname = 'lattice.latticeuntorsion'
	bl_label = 'LatticeUntorsion'
	bl_options = {'REGISTER', 'UNDO'}
	lastRun = 0

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'LATTICE')
		
	def execute(self, context):
		pass
		#print ("execute>" , context)
		
	def invoke(self, context, event):
		context.window_manager.modal_handler_add(self)
		self._timer = context.window_manager.event_timer_add(1.0, context.window)
		return {'RUNNING_MODAL'}

	def cancel(self, context):
		context.window_manager.event_timer_remove(self._timer)
		return {'CANCELLED'}
		
	def modal(self, context, event):
		#print (event.type, bpy.context.mode)
		if bpy.context.mode != 'EDIT_LATTICE':
			return {'CANCELLED'}
		if event.type == 'TIMER':
			timeNow = time.time()
			if timeNow - LatticeUnTorsion.lastRun < 0.25:
				return {'PASS_THROUGH'}
			LatticeUnTorsion.lastRun = time.time()
			activeLattice = bpy.context.active_object
			lu = activeLattice.data.points_u
			lv = activeLattice.data.points_v
			lw = activeLattice.data.points_w
			#selected = []
			#for i in range(len(activeLattice.data.points)):
			#	index_u = i % lu
			#	index_v = (i // lu) % lv
			#	index_w = (i // lu // lv) % lw
			#	if activeLattice.data.points[i].select:
			#		selected.append(i)
			#	#print(i,index_u,index_v,index_w,activeLattice.data.points[i].select)
			##print ('selected',selected)
			selected = [i for i in range(len(activeLattice.data.points)) if activeLattice.data.points[i].select]
			#print (selected2)
			# pivot 
			if len(selected) < 2:
				return {'PASS_THROUGH'}
			pivot = Vector((0,0,0))
			for i in selected:
				pivot += activeLattice.data.points[i].co_deform
			pivot /= len(selected)
			#print ('pivot',pivot)
			# das hier muß eine eigene Funktion werden, die die NachbarIndezes zu einem Lattice ermittelt
			# Funktion (start)
			index_to_n = {}
			dirs = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]
			for i in selected:
				index_to_n[i] = []
				index_u = i % lu
				index_v = (i // lu) % lv
				index_w = (i // lu // lv) % lw
				for diri in range(len(dirs)):
					index_u_n = index_u+dirs[diri][0]
					index_v_n = index_v+dirs[diri][1]
					index_w_n = index_w+dirs[diri][2]
					#print (index_u,index_v,index_w, index_u_n,index_v_n,index_w_n)
					if 0 <= index_u_n and 0 <= index_v_n and 0 <= index_w_n \
						and index_u_n < lu and index_v_n < lv and index_w_n < lw:
						i_n = index_w_n * lu * lv + index_v_n * lu + index_u_n
						if activeLattice.data.points[i_n].select == False:
							index_to_n[i].append(i_n)
						#activeLattice.data.points[i_n].select = True
						#print (i, dirs[diri])
			#print ('index_to_n',index_to_n)
			w = {1:0.0 , 2:0.0 , 3: 0.0}
			maxCount = 50
			final = {}
			meanErrorRaw = 1000
			erg = []
			while 0 < maxCount:
				#print ()
				#print ('******************')
				maxCount -= 1
				erg = []
				for i,vv in index_to_n.items():
					point_t = activeLattice.data.points[i].co_deform
					#print ("point_t",point_t)
					for i_traj in vv:
						point_t_traj = activeLattice.data.points[i_traj].co_deform
						traj_point = point({1:point_t_traj.x, 2:point_t_traj.y, 3:point_t_traj.z})
						#print (point_t.x,point_t.y,point_t.z,vv)
						#a1 = point({1:1, 2:0, 3:1})
						#a2 = point({1:1, 2:0, 3:-1})

						t = trajectory({1:point_t.x, 2:point_t.y, 3:point_t.z})
						t.setOffset({1:pivot.x, 2:pivot.y, 3:pivot.z})
						t.setTrajectoryPoint(traj_point)
						t.setRotation(w)
						h = t.getH()
						d = t.getD()
						final[i] = t.getTrajectoryPoint();
						erg.append({'h': h, 'd': d})
						#print ('height',h)
						#print ('dev',d)
				m = matrix()
				t = []
				for i,v in enumerate(erg):
					#print (i,v)
					m.set(i,0,v['d'][1])
					m.set(i,1,v['d'][2])
					m.set(i,2,v['d'][3])
					t.append(v['h'])
				#print ('m')
				#m.write()
				ma = m.t_copy().mul_matrix(m)
				#print ('ma')
				#ma.write()
				#print ('t', t)
				vb = m.t_copy().mul_vektor(t)
				#print ('vb', vb)
				ee = ma.gauss(vb)
				#print ('ee',ee)
				maxmov = 0.0001
				meanErrorRaw = ee[0]*ee[0] + ee[1]*ee[1] + ee[2]*ee[2]
				for i in range(len(ee)):
					if ee[i] < -maxmov:
						ee[i] = -maxmov
					if ee[i] > maxmov:
						ee[i] = maxmov
				meanError = ee[0]*ee[0] + ee[1]*ee[1] + ee[2]*ee[2]
				#print ('ee maxmov',ee)
				w = {1: w[1] - ee[0] , 2: w[2] - ee[1] , 3: w[3] - ee[2]}
				#print ('w',maxCount, "%6.7f" % w[1],"%6.7f" % w[2],"%6.7f" % w[3],"%6.7f" % meanErrorRaw)
				if meanError < 1e-9:
					maxCount = min(1,maxCount)
			#print ('final', final)
			#for e in erg:
			#	#print (e['h'])
			#print (time.time(), "meanError", meanErrorRaw)
			for i,vv in final.items():
				activeLattice.data.points[i].co_deform.x = vv[1]
				activeLattice.data.points[i].co_deform.y = vv[2]
				activeLattice.data.points[i].co_deform.z = vv[3]
			LatticeUnTorsion.lastRun = time.time()
			#return {'CANCELLED'}
		return {'PASS_THROUGH'}

class LatticeBind(bpy.types.Operator):
	'''Bind a Mesh to a Lattice'''
	bl_idname = 'lattice.bind'
	bl_label = 'LatticeBind'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		active = bpy.context.active_object
		minX, maxX, minY, maxY, minZ, maxZ = 10000, -10000, 10000, -10000, 10000, -10000
		for v in active.data.vertices:
			#cov = (active.matrix_basis * v.co.to_4d()).to_3d()
			cov = v.co
			#print (o.name, cov, (co.to_3d() - cov).length)
			minX, maxX = min(minX, cov.x), max(maxX, cov.x)
			minY, maxY = min(minY, cov.y), max(maxY, cov.y)
			minZ, maxZ = min(minZ, cov.z), max(maxZ, cov.z)
		dx, dy, dz = maxX - minX, maxY - minY, maxZ - minZ
		dx2, dy2, dz2 = 1.0, 1.0, 1.0
		bpy.ops.object.duplicate(linked=True, mode='TRANSLATION')
		new_active = bpy.context.active_object
		#bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
		new_active.rotation_euler = mathutils.Euler((0.0, 0.0, 0.0), 'XYZ')
		ddx = 1.0
		if abs(dx) < 1e-6:
			pdx, dx, dx2 = - minX, 1.0, 0.0
		else:
			ddx = 1.0 / dx
			pdx = - minX * ddx - 0.5
		ddy = 1.0
		if abs(dy) < 1e-6:
			pdy, dy, dy2 = - minY, 1.0, 0.0
		else:
			ddy = 1.0 / dy
			pdy = - minY * ddy - 0.5
		ddz = 1.0
		if abs(dz) < 1e-6:
			pdz, dz, dz2 = - minZ, 1.0, 0.0
		else:
			ddz = 1.0 / dz
			pdz = - minZ * ddz - 0.5
		#print (minX, new_active.location.x, ddx)
		#print ('Location',pdx, pdy, pdz)
		#print ('Scale',ddx, ddy, ddz)
		new_active.location = Vector((pdx, pdy, pdz))
		new_active.scale = Vector((ddx, ddy, ddz))
		ob_new = bpy.data.lattices.new("bnd_lattice")
		latticeObj = bpy.data.objects.new("bnd_lattice", ob_new)
		bpy.context.scene.objects.link(latticeObj)
		lattice = new_active.modifiers.new("bnd_lattice", "LATTICE")
		lattice.object = latticeObj
		lattice.show_in_editmode = True
		lattice.show_on_cage = True
		latticeObj.data.interpolation_type_u = "KEY_LINEAR"
		latticeObj.data.interpolation_type_v = "KEY_LINEAR"
		latticeObj.data.interpolation_type_w = "KEY_LINEAR"
		for lv in latticeObj.data.points:
			bv = Vector(((lv.co_deform.x + 0.5 * dx2) * dx+ minX, (lv.co_deform.y + 0.5 * dy2)* dy + minY, (lv.co_deform.z + 0.5 * dz2) * dz + minZ))
			lv.co_deform = (active.matrix_basis * bv.to_4d()).to_3d()
		copy_transforms = new_active.constraints.new("COPY_LOCATION")
		copy_transforms.target = latticeObj
		copy_transforms.use_offset = True
		copy_transforms.use_x = True
		copy_transforms.use_y = True
		copy_transforms.use_z = True
		return {'FINISHED'}

class VIEW3D_PT_tools_LatticeForge(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = "objectmode"
	bl_idname = 'LatticeForge'
	bl_label = "Lattice Forge"
	bl_category = "Relations"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		active_obj = context.active_object
		layout = self.layout

		col = layout.column(align=True)
		row = col.row(align=True)
		row.operator("lattice.bind", text="Bind Lattice")
		row.operator("lattice.rebind", text="Rebind Lattice")
		col.operator("lattice.unbind", text="Apply Lattice")

		#row = col.row()
		col = layout.column(align=True)
		col.prop(context.scene, "lattice_dir")

		#col2 = layout.column(align=True)
		col = layout.column(align=True)
		col.operator("lattice.latticeaddcubic", text="Cubic *2 add Points")

		#col = layout.column(align=True)
		#col.operator("lattice.latticeremesh", text="remesh")
		
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(context.scene, "lattice_reorder_samplesmode")
		row.prop(context.scene, "lattice_reorder_samples")
		col.operator("lattice.latticecubicreorder", text="Reorder Cubic")
		
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(context.scene, "lattice_add_samplesmode")
		row.prop(context.scene, "lattice_add_samples")
		col.operator("lattice.latticelinearadd", text="Add Points")
		
		col = layout.column(align=True)
		col.prop(context.scene, "lattice_forgedir")
		col.operator("lattice.latticeforgeplanar", text="planar diff dir")
		col.operator("lattice.latticeforgemultiplanar", text="planar same dir")
		
		#col = layout.column(align=True)
		#col.operator("lattice.latticeuntorsion", text="untorsion")
		#col = layout.column(align=True)
		#col.operator("lattice.untension", text="untension")
		col = layout.column(align=True)
		col.label("Surfaces")
		col.operator("surface.bind", text="bind Surface")
		col.operator("surface.apply", text="apply Surface")
		col.operator("surface.unbind", text="unbind Surface")

class VIEW3D_PT_tools_LatticeTorsion(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_context = "lattice_edit"
	bl_idname = 'LatticeTorsion'
	bl_label = "Lattice Torsion"
	bl_category = "Relations"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		active_obj = context.active_object
		layout = self.layout

		col = layout.column(align=True)
		col.operator("lattice.latticeuntorsion", text="untorsion")
		
		#col = layout.column(align=True)
		#col.operator("lattice.latticetest", text="test")

		#col = layout.column(align=True)
		#col.operator("lattice.untension", text="untension")

classes = [VIEW3D_PT_tools_LatticeForge,
	VIEW3D_PT_tools_LatticeTorsion,
	SurfaceBind,
	SurfaceUnbind,
	SurfaceApply,
	LatticeBind,
	LatticeReBind,
	LatticeUnBind,
	LatticeAddCubic,
	LatticeRemesh,
	LatticeUnTorsion,
	LatticeTest,
	LatticeCubicReorder,
	LatticeLinearAdd,
	LatticeForgePlanar,
	LatticeForgeMultiPlanar,]

def register():
	#bpy.utils.register_module(__name__)
	for c in classes:
		bpy.utils.register_class(c)
	bpy.types.Scene.lattice_dir = EnumProperty(
		name="",
		description="Direction of the Lattice",
		items=[("u","u","u-dir"),
			("v","v","v-dir"),
			("w","w","w-dir"),
			],
		default='u')
	bpy.types.Scene.lattice_add_samples = IntProperty(
		name="points",
		description="Points to Add",
		default = 12,
		min = 1,
		max = 64)
	bpy.types.Scene.lattice_add_samplesmode = BoolProperty(
		name="individual",
		description="varying amounts of point per section",
		default = True)
	bpy.types.Scene.lattice_reorder_samples = IntProperty(
		name="points",
		description="Points to Reorder",
		default = 12,
		min = 3,
		max = 64)
	bpy.types.Scene.lattice_reorder_samplesmode = BoolProperty(
		name="individual",
		description="Points to Reorder",
		default = True)
	bpy.types.Scene.lattice_forgedir = EnumProperty(
		name="",
		description="Direction of the Lattice",
		items=[("u","u","u-dir"),
			("v","v","v-dir"),
			("w","w","w-dir"),
			],
		default='u')

def unregister():
	#bpy.utils.unregister_module(__name__)
	for c in classes:
		bpy.utils.unregister_class(c)
	del bpy.types.Scene.lattice_dir

if __name__ == "__main__":
	register()
	logging.basicConfig(filename='c:\\tmp\\python.txt', format='%(message)s', level=logging.DEBUG)