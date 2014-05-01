# -*- coding: cp1252 -*-
from math import *
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
                e += "%10.5f" % v2
            print (e)

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
        # backward-Schritt
        lin = False
        for i in range(len(self.field)-1,0,-1):
            #print ("backward",i)
            #self.write()
            #print (e)
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
    w = {1: 0.0, 2:0.0, 3:0.0}
    trajectoryPoint = None
    verbose = 1
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

    def log(self, text=''):
        print (text)
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
            # Rotationmatrix multiplied with targetvector (this is vector one we do refer to)
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
            #
                
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

    
#a1 = point({1:1, 2:1, 3:0})
#a2 = point({1:1, 2:-1, 3:0})
a1 = point({1:1.1, 2:1.3, 3:0.7})
#a2 = point({1:1, 2:0, 3:-1})
a1 = point({1:1.0, 2:1.0, 3:0.0})

#t = trajectory({1:1.0, 2:0.2, 3:0.1})
t = trajectory({1:0.5, 2:0.5, 3:0.0})

t.setOffset({1:0.0, 2:0.0, 3:0.0})
t.setTrajectoryPoint(a1)

#w = {1:0.0 , 2:0.0 , 3: 0.0}
w = {1:0.5 , 2:0.7 , 3: -0.73}

t.setRotation(w)

t.calculate()

##h = t.getH()
##d = t.getD()
##m = matrix()
##m.set(0,0,d[0])
##m.set(0,1,d[1])
##m.set(0,2,d[2])
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



       
