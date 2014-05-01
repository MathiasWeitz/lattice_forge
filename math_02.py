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
    trajectoryPoints = []
    verbose = 0
    h = 0.0
    diff = (0.0, 0.0, 0.0)
    isCalculated = False

    def __init__(self, point):
        self.point = point

    def setTrajectoryPoints(self, points):
        self.trajectoryPoints = points
        
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

    def calculate(self):
        if not self.isCalculated:
            p = {}
            for i, pp in enumerate(self.trajectoryPoints):
                p[i+1] = pp.coor()
                p[i+1][1] -= self.offset[1]
                p[i+1][2] -= self.offset[2]
                p[i+1][3] -= self.offset[3]
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
            
            zug = {}
            zugdist = {}
            zugdist_diffx = {}
            zugdist_diffy = {}
            zugdist_diffz = {}
            zugnorm_diffx = {}
            zugnorm_diffy = {}
            zugnorm_diffz = {}
            zugnorm = {}
            zugsum = {1:0.0, 2:0.0, 3:0.0}
            zugNormSum_diffx = {1:0.0, 2:0.0, 3:0.0}
            zugNormSum_diffy = {1:0.0, 2:0.0, 3:0.0}
            zugNormSum_diffz = {1:0.0, 2:0.0, 3:0.0}
            for i,vv in p.items():
                # difference to the trajecting point
                zug[i] = {1:vv[1] - vp[1],2:vv[2] - vp[2],3:vv[3] - vp[3]}
                sum1 = zug[i][1] * zug[i][1]
                sum2 = zug[i][2] * zug[i][2]
                sum3 = zug[i][3] * zug[i][3]
                # distance
                zugdist[i] = sqrt(sum1 + sum2 + sum3)
                zugdist3 = zugdist[i] * (sum1 + sum2 + sum3)
                # derivative of the distance
                zugdist_diffx[i] = -(Mp_diffx[1] * zug[i][1] + Mp_diffx[2] * zug[i][2] + Mp_diffx[3] * zug[i][3]) / zugdist[i]
                zugdist_diffy[i] = -(Mp_diffy[1] * zug[i][1] + Mp_diffy[2] * zug[i][2] + Mp_diffy[3] * zug[i][3]) / zugdist[i]
                zugdist_diffz[i] = -(Mp_diffz[1] * zug[i][1] + Mp_diffz[2] * zug[i][2] + Mp_diffz[3] * zug[i][3]) / zugdist[i]
                # derivative of the normalized trajectory
                zugnorm_diffx[i] = {}
                zugnorm_diffx[i][1] = - Mp_diffx[1] / zugdist[i] + zug[i][1] * (Mp_diffx[1] * zug[i][1] + Mp_diffx[2] * zug[i][2] + Mp_diffx[3] * zug[i][3]) / zugdist3
                zugnorm_diffx[i][2] = - Mp_diffx[2] / zugdist[i] + zug[i][2] * (Mp_diffx[1] * zug[i][1] + Mp_diffx[2] * zug[i][2] + Mp_diffx[3] * zug[i][3]) / zugdist3
                zugnorm_diffx[i][3] = - Mp_diffx[3] / zugdist[i] + zug[i][3] * (Mp_diffx[1] * zug[i][1] + Mp_diffx[2] * zug[i][2] + Mp_diffx[3] * zug[i][3]) / zugdist3
                zugnorm_diffy[i] = {}
                zugnorm_diffy[i][1] = - Mp_diffy[1] / zugdist[i] + zug[i][1] * (Mp_diffy[1] * zug[i][1] + Mp_diffy[2] * zug[i][2] + Mp_diffy[3] * zug[i][3]) / zugdist3
                zugnorm_diffy[i][2] = - Mp_diffy[2] / zugdist[i] + zug[i][2] * (Mp_diffy[1] * zug[i][1] + Mp_diffy[2] * zug[i][2] + Mp_diffy[3] * zug[i][3]) / zugdist3
                zugnorm_diffy[i][3] = - Mp_diffy[3] / zugdist[i] + zug[i][3] * (Mp_diffy[1] * zug[i][1] + Mp_diffy[2] * zug[i][2] + Mp_diffy[3] * zug[i][3]) / zugdist3
                zugnorm_diffz[i] = {}
                zugnorm_diffz[i][1] = - Mp_diffz[1] / zugdist[i] + zug[i][1] * (Mp_diffz[1] * zug[i][1] + Mp_diffz[2] * zug[i][2] + Mp_diffz[3] * zug[i][3]) / zugdist3
                zugnorm_diffz[i][2] = - Mp_diffz[2] / zugdist[i] + zug[i][2] * (Mp_diffz[1] * zug[i][1] + Mp_diffz[2] * zug[i][2] + Mp_diffz[3] * zug[i][3]) / zugdist3
                zugnorm_diffz[i][3] = - Mp_diffz[3] / zugdist[i] + zug[i][3] * (Mp_diffz[1] * zug[i][1] + Mp_diffz[2] * zug[i][2] + Mp_diffz[3] * zug[i][3]) / zugdist3
                
                zugnorm[i] = {}
                zugnorm[i][1] = zug[i][1] / zugdist[i]
                zugnorm[i][2] = zug[i][2] / zugdist[i]
                zugnorm[i][3] = zug[i][3] / zugdist[i]
                zugsum[1] += zugnorm[i][1]
                zugsum[2] += zugnorm[i][2]
                zugsum[3] += zugnorm[i][3]
                # make a sum of all what is needed
                zugNormSum_diffx[1] += zugnorm_diffx[i][1]
                zugNormSum_diffx[2] += zugnorm_diffx[i][2]
                zugNormSum_diffx[3] += zugnorm_diffx[i][3]
                zugNormSum_diffy[1] += zugnorm_diffy[i][1]
                zugNormSum_diffy[2] += zugnorm_diffy[i][2]
                zugNormSum_diffy[3] += zugnorm_diffy[i][3]
                zugNormSum_diffz[1] += zugnorm_diffz[i][1]
                zugNormSum_diffz[2] += zugnorm_diffz[i][2]
                zugNormSum_diffz[3] += zugnorm_diffz[i][3]

            ZugSumDist = sqrt(zugsum[1]*zugsum[1] + zugsum[2]*zugsum[2] + zugsum[3]*zugsum[3])
            ZugSumNorm = {1:zugsum[1], 2:zugsum[2], 3:zugsum[3]}
            if 0 < ZugSumDist:
                ZugSumNorm = {1:zugsum[1]/ZugSumDist, 2:zugsum[2]/ZugSumDist, 3:zugsum[3]/ZugSumDist }
            # height (equals misalignment) as a vector
            h = {1: vp[3]*ZugSumNorm[2]-vp[2]*ZugSumNorm[3],2: vp[1]*ZugSumNorm[3]-vp[3]*ZugSumNorm[1], 3: vp[2]*ZugSumNorm[1] - vp[1]*ZugSumNorm[2]}
            hh = h[1]*h[1] + h[2]*h[2] + h[3]*h[3]
            # height as a distance, this value is a measurement for the error, it should get zero
            shh = sqrt(hh)

            ZugSumDist_diffx, ZugSumDist_diffy, ZugSumDist_diffz = 0,0,0
            ZugSumNorm_diffx = {1:0.0, 2:0.0, 3:0.0}
            ZugSumNorm_diffy = {1:0.0, 2:0.0, 3:0.0}
            ZugSumNorm_diffz = {1:0.0, 2:0.0, 3:0.0}
            if 0 < ZugSumDist:
                ZugSumDist_diffx = (zugsum[1] * zugNormSum_diffx[1] + zugsum[2] * zugNormSum_diffx[2] + zugsum[3] * zugNormSum_diffx[3]) / ZugSumDist
                ZugSumDist_diffy = (zugsum[1] * zugNormSum_diffy[1] + zugsum[2] * zugNormSum_diffy[2] + zugsum[3] * zugNormSum_diffy[3]) / ZugSumDist
                ZugSumDist_diffz = (zugsum[1] * zugNormSum_diffz[1] + zugsum[2] * zugNormSum_diffz[2] + zugsum[3] * zugNormSum_diffz[3]) / ZugSumDist

                ZugSumDist3 = ZugSumDist * ZugSumDist * ZugSumDist
                ZugSumNorm_diffx = {}
                ZugSumNorm_diffx[1] = zugNormSum_diffx[1] / ZugSumDist - zugsum[1] * (zugNormSum_diffx[1] * zugsum[1] + zugNormSum_diffx[2] * zugsum[2] + zugNormSum_diffx[3] * zugsum[3]) / ZugSumDist3
                ZugSumNorm_diffx[2] = zugNormSum_diffx[2] / ZugSumDist - zugsum[2] * (zugNormSum_diffx[1] * zugsum[1] + zugNormSum_diffx[2] * zugsum[2] + zugNormSum_diffx[3] * zugsum[3]) / ZugSumDist3
                ZugSumNorm_diffx[3] = zugNormSum_diffx[3] / ZugSumDist - zugsum[3] * (zugNormSum_diffx[1] * zugsum[1] + zugNormSum_diffx[2] * zugsum[2] + zugNormSum_diffx[3] * zugsum[3]) / ZugSumDist3
                ZugSumNorm_diffy = {}
                ZugSumNorm_diffy[1] = zugNormSum_diffy[1] / ZugSumDist - zugsum[1] * (zugNormSum_diffy[1] * zugsum[1] + zugNormSum_diffy[2] * zugsum[2] + zugNormSum_diffy[3] * zugsum[3]) / ZugSumDist3
                ZugSumNorm_diffy[2] = zugNormSum_diffy[2] / ZugSumDist - zugsum[2] * (zugNormSum_diffy[1] * zugsum[1] + zugNormSum_diffy[2] * zugsum[2] + zugNormSum_diffy[3] * zugsum[3]) / ZugSumDist3
                ZugSumNorm_diffy[3] = zugNormSum_diffy[3] / ZugSumDist - zugsum[3] * (zugNormSum_diffy[1] * zugsum[1] + zugNormSum_diffy[2] * zugsum[2] + zugNormSum_diffy[3] * zugsum[3]) / ZugSumDist3
                ZugSumNorm_diffz = {}
                ZugSumNorm_diffz[1] = zugNormSum_diffz[1] / ZugSumDist - zugsum[1] * (zugNormSum_diffz[1] * zugsum[1] + zugNormSum_diffz[2] * zugsum[2] + zugNormSum_diffz[3] * zugsum[3]) / ZugSumDist3
                ZugSumNorm_diffz[2] = zugNormSum_diffz[2] / ZugSumDist - zugsum[2] * (zugNormSum_diffz[1] * zugsum[1] + zugNormSum_diffz[2] * zugsum[2] + zugNormSum_diffz[3] * zugsum[3]) / ZugSumDist3
                ZugSumNorm_diffz[3] = zugNormSum_diffz[3] / ZugSumDist - zugsum[3] * (zugNormSum_diffz[1] * zugsum[1] + zugNormSum_diffz[2] * zugsum[2] + zugNormSum_diffz[3] * zugsum[3]) / ZugSumDist3

            h_diffx = {1: vp[3]*ZugSumNorm_diffx[2] + Mp_diffx[3] * ZugSumNorm[2] - vp[2]*ZugSumNorm_diffx[3] - Mp_diffx[2]*ZugSumNorm[3], \
                       2: vp[1]*ZugSumNorm_diffx[3] + Mp_diffx[1] * ZugSumNorm[3] - vp[3]*ZugSumNorm_diffx[1] - Mp_diffx[3]*ZugSumNorm[1], \
                       3: vp[2]*ZugSumNorm_diffx[1] + Mp_diffx[2] * ZugSumNorm[1] - vp[1]*ZugSumNorm_diffx[2] - Mp_diffx[1]*ZugSumNorm[2]}
            h_diffy = {1: vp[3]*ZugSumNorm_diffy[2] + Mp_diffy[3] * ZugSumNorm[2] - vp[2]*ZugSumNorm_diffy[3] - Mp_diffy[2]*ZugSumNorm[3], \
                       2: vp[1]*ZugSumNorm_diffy[3] + Mp_diffy[1] * ZugSumNorm[3] - vp[3]*ZugSumNorm_diffy[1] - Mp_diffy[3]*ZugSumNorm[1], \
                       3: vp[2]*ZugSumNorm_diffy[1] + Mp_diffy[2] * ZugSumNorm[1] - vp[1]*ZugSumNorm_diffy[2] - Mp_diffy[1]*ZugSumNorm[2]}
            h_diffz = {1: vp[3]*ZugSumNorm_diffz[2] + Mp_diffz[3] * ZugSumNorm[2] - vp[2]*ZugSumNorm_diffz[3] - Mp_diffz[2]*ZugSumNorm[3], \
                       2: vp[1]*ZugSumNorm_diffz[3] + Mp_diffz[1] * ZugSumNorm[3] - vp[3]*ZugSumNorm_diffz[1] - Mp_diffz[3]*ZugSumNorm[1], \
                       3: vp[2]*ZugSumNorm_diffz[1] + Mp_diffz[2] * ZugSumNorm[1] - vp[1]*ZugSumNorm_diffz[2] - Mp_diffz[1]*ZugSumNorm[2]}
            hh_diffx = 2*h[1]*h_diffx[1] + 2*h[2]*h_diffx[2] + 2*h[3]*h_diffx[3]
            hh_diffy = 2*h[1]*h_diffy[1] + 2*h[2]*h_diffy[2] + 2*h[3]*h_diffy[3]
            hh_diffz = 2*h[1]*h_diffz[1] + 2*h[2]*h_diffz[2] + 2*h[3]*h_diffz[3]
            # the derivative of the norm of the height
            shh_diffx, shh_diffy, shh_diffz = 0,0,0
            if 0.0 != shh:
                shh_diffx = 0.5 * hh_diffx / shh
                shh_diffy = 0.5 * hh_diffy / shh
                shh_diffz = 0.5 * hh_diffz / shh

            self.h = shh
            self.diff = (shh_diffx, shh_diffy, shh_diffz)
            self.isCalculated = True
                
            if 1 == self.verbose:
                # nomenklatura for wxmaxima
                print ("load(vect);")
                print ("define (Ax(w), matrix([1,0,0],[0,cos(w[1]),-sin(w[1])],[0,sin(w[1]),cos(w[1])]));")
                print ("define (Ay(w), matrix([cos(w[2]),0,-sin(w[2])],[0,1,0],[sin(w[2]),0,cos(w[2])]));")
                print ("define (Az(w), matrix([cos(w[3]),-sin(w[3]),0],[sin(w[3]),cos(w[3]),0],[0,0,1]));")
                print ("define (M(w), Az(w).Ay(w).Ax(w));")
                print ("define(V(v),matrix([v[1],v[2],v[3]]));")
                print ("define(Mp(w,V), M(w).V);")
                
                for ip,pp in p.items():
                    print ("P" + str(ip) + ":[" + str(pp[1]) + "," + str(pp[2]) + "," + str(pp[3]) + "];")
                    print ("define(Zug" + str(ip) + "(w,v), P" + str(ip) + " - Mp(w,v));")
                    print ("define(Zug" + str(ip) + "Dist(w,v), sqrt(Zug" + str(ip) + "(w,v).Zug" + str(ip) + "(w,v)));")
                    print ("define(Zug" + str(ip) + "Norm(w,v), Zug" + str(ip) + "(w,v)/Zug" + str(ip) + "Dist(w,v));")

                zugsumS = []
                for i,vv in zugnorm.items():
                    zugsumS.append("Zug"+str(i)+"Norm(w,v)")
                print ("define(ZugSum(w,v)," + ' + '.join(zugsumS) + ");")
                print ("define(ZugSumDist(w,v), sqrt(ZugSum(w,v).ZugSum(w,v)));")
                print ("define(ZugSumNorm(w,v),ZugSum(w,v) / ZugSumDist(w,v));")
                print ("define(h(w,v), express(list_matrix_entries(ZugSumNorm(w,V(v))) ~ list_matrix_entries(Mp(w,V(v)))));")
                print ("define(hh(w,v), h(w,v).h(w,v));")
                print ("define(shh(w,v), sqrt(hh(w,v)));")
                print ("define(Mp_diffx(w,v), diff(Mp(w,V(v)),w[1]));")
                print ("define(Mp_diffy(w,v), diff(Mp(w,V(v)),w[2]));")
                print ("define(Mp_diffz(w,v), diff(Mp(w,V(v)),w[3]));")
                for i,vv in zugnorm.items():
                    print ("define(Zug"+str(i)+"Dist_diffx(w,v), diff(sqrt(Zug"+str(i)+"(w,V(v)).Zug"+str(i)+"(w,V(v))),w[1]));")
                    print ("define(Zug"+str(i)+"Dist_diffy(w,v), diff(sqrt(Zug"+str(i)+"(w,V(v)).Zug"+str(i)+"(w,V(v))),w[2]));")
                    print ("define(Zug"+str(i)+"Dist_diffz(w,v), diff(sqrt(Zug"+str(i)+"(w,V(v)).Zug"+str(i)+"(w,V(v))),w[3]));")
                    print ("define(Zug"+str(i)+"Norm_diffx(w,v), diff(Zug"+str(i)+"(w,V(v)) / sqrt(Zug"+str(i)+"(w,V(v)).Zug"+str(i)+"(w,V(v))),w[1]));")
                    print ("define(Zug"+str(i)+"Norm_diffy(w,v), diff(Zug"+str(i)+"(w,V(v)) / sqrt(Zug"+str(i)+"(w,V(v)).Zug"+str(i)+"(w,V(v))),w[2]));")
                    print ("define(Zug"+str(i)+"Norm_diffz(w,v), diff(Zug"+str(i)+"(w,V(v)) / sqrt(Zug"+str(i)+"(w,V(v)).Zug"+str(i)+"(w,V(v))),w[3]));")
                print ("define(ZugSum_diffx(w,v), diff(ZugSum(w,V(v)),w[1]));")
                print ("define(ZugSum_diffy(w,v), diff(ZugSum(w,V(v)),w[2]));")
                print ("define(ZugSum_diffz(w,v), diff(ZugSum(w,V(v)),w[3]));")
                print ("define(ZugSumDist_diffx(w,v), diff(ZugSumDist(w,V(v)),w[1]));")
                print ("define(ZugSumDist_diffy(w,v), diff(ZugSumDist(w,V(v)),w[2]));")
                print ("define(ZugSumDist_diffz(w,v), diff(ZugSumDist(w,V(v)),w[3]));")
                print ("define(ZugSumNorm_diffx(w,v), diff(ZugSumNorm(w,V(v)),w[1]));")
                print ("define(ZugSumNorm_diffy(w,v), diff(ZugSumNorm(w,V(v)),w[2]));")
                print ("define(ZugSumNorm_diffz(w,v), diff(ZugSumNorm(w,V(v)),w[3]));")
                print ("define(h_diffx(w,v), diff(h(w,v),w[1]));")
                print ("define(h_diffy(w,v), diff(h(w,v),w[2]));")
                print ("define(h_diffz(w,v), diff(h(w,v),w[3]));")
                print ("define(hh_diffx(w,v), diff(hh(w,v),w[1]));")
                print ("define(hh_diffy(w,v), diff(hh(w,v),w[2]));")
                print ("define(hh_diffz(w,v), diff(hh(w,v),w[3]));")
                print ("define(shh_diffx(w,v), diff(shh(w,v),w[1]));")
                print ("define(shh_diffy(w,v), diff(shh(w,v),w[2]));")
                print ("define(shh_diffz(w,v), diff(shh(w,v),w[3]));")

                # putting in values for checking
                print()
                arg = '[' + str(w[1]) +  ',' +  str(w[2]) + ',' +  str(w[3]) +'],[' + str(v[1]) + ',' +  str(v[2]) + ',' + str(v[3]) + ']'
                print("Mp(" + arg + ") = ", vp)
                for i,vv in zug.items():
                    print ("Zug"+str(i)+"(" + arg + ")", vv)
                for i,vv in zugdist.items():
                    print ("Zug"+str(i)+"Dist(" + arg + ")", vv)
                for i,vv in zugnorm.items():
                    print ("Zug"+str(i)+"Norm(" + arg + ")", vv)

                print ("ZugSum(" + arg + ")", zugsum)
                print ("ZugSumDist(" + arg + ")", ZugSumDist)
                print ("ZugSumNorm(" + arg + ")", ZugSumNorm)

                print ("h(" + arg + ")", h)
                print ("hh(" + arg + ")", hh)
                print ("shh(" + arg + ")", shh)

                print ("**** Ableitung ****")

                print ("Mp_diffx(" + arg + ")", Mp_diffx)
                print ("Mp_diffy(" + arg + ")", Mp_diffy)
                print ("Mp_diffz(" + arg + ")", Mp_diffz)
                for i,vv in zugnorm.items():
                    print ("Zug"+str(i)+"Dist_diffx(" + arg + ")", zugdist_diffx[i])
                    print ("Zug"+str(i)+"Dist_diffy(" + arg + ")", zugdist_diffy[i])
                    print ("Zug"+str(i)+"Dist_diffz(" + arg + ")", zugdist_diffz[i])
                    print ("Zug"+str(i)+"Norm_diffx(" + arg + ")", zugnorm_diffx[i])
                    print ("Zug"+str(i)+"Norm_diffy(" + arg + ")", zugnorm_diffy[i])
                    print ("Zug"+str(i)+"Norm_diffz(" + arg + ")", zugnorm_diffz[i])
                print ("ZugSum_diffx(" + arg + ")", zugNormSum_diffx[1] , zugNormSum_diffx[2] , zugNormSum_diffx[3])
                print ("ZugSum_diffy(" + arg + ")", zugNormSum_diffy[1] , zugNormSum_diffy[2] , zugNormSum_diffy[3])
                print ("ZugSum_diffz(" + arg + ")", zugNormSum_diffz[1] , zugNormSum_diffz[2] , zugNormSum_diffz[3])

                print ("ZugSumDist_diffx(" + arg + ")", ZugSumDist_diffx)
                print ("ZugSumDist_diffy(" + arg + ")", ZugSumDist_diffy)
                print ("ZugSumDist_diffz(" + arg + ")", ZugSumDist_diffz)

                print ("ZugSumNorm_diffx(" + arg + ")", ZugSumNorm_diffx)
                print ("ZugSumNorm_diffy(" + arg + ")", ZugSumNorm_diffy)
                print ("ZugSumNorm_diffz(" + arg + ")", ZugSumNorm_diffz)
                print ("h_diffx(" + arg + ")", h_diffx)
                print ("h_diffy(" + arg + ")", h_diffy)
                print ("h_diffz(" + arg + ")", h_diffz)
                print ("hh_diffx(" + arg + ")", hh_diffx)
                print ("hh_diffy(" + arg + ")", hh_diffy)
                print ("hh_diffz(" + arg + ")", hh_diffz)
                print ("shh_diffx(" + arg + ")", shh_diffx)
                print ("shh_diffy(" + arg + ")", shh_diffy)
                print ("shh_diffz(" + arg + ")", shh_diffz)

        
    
#a1 = point({1:1, 2:1, 3:0})
#a2 = point({1:1, 2:-1, 3:0})
a1 = point({1:1, 2:0, 3:1})
a2 = point({1:1, 2:0, 3:-1})

t = trajectory({1:0.0, 2:2.0, 3:0.0})

t.setOffset({1:0.0, 2:0.0, 3:0.0})
t.setTrajectoryPoints([a1, a2])

w = {1:0.04 , 2:0.1 , 3: -1.58}

t.setRotation(w)

#t.calculate()

h = t.getH()
d = t.getD()
m = matrix()
m.set(0,0,d[0])
m.set(0,1,d[1])
m.set(0,2,d[2])

t=[h]

print ("ergH", h)
print ("ergD", d)
m.write()
print ()
ma = m.t_copy().mul_matrix(m)
ma.write()
print ()
vb = m.t_copy().mul_vektor(t)
print (vb)

print ()
ee = ma.gauss(vb)
print (ee)



       
