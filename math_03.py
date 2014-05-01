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
            # just a joke, the distance of a vector in a rotationmatrix never changes
            distz_diffx = 0.0
            distz_diffy = 0.0
            distz_diffz = 0.0

            normz_diffx = {1: Mp_diffx[1] / distz, 2: Mp_diffx[2] / distz, 3: Mp_diffx[3] / distz}
            normz_diffy = {1: Mp_diffy[1] / distz, 2: Mp_diffy[2] / distz, 3: Mp_diffy[3] / distz}
            normz_diffz = {1: Mp_diffz[1] / distz, 2: Mp_diffz[2] / distz, 3: Mp_diffz[3] / distz}
            
            h_diff = {1:{},2:{},3:{}}
            hh_diff = {}
            hn_diff = {}
            target_diff = {}
            # difference to the trajecting point
            zug = {1:p[1] - vp[1],2:p[2] - vp[2],3:p[3] - vp[3]}
            h = {1: zug[2]*normz[3] - zug[3]*normz[2],
                2: zug[3]*normz[1] - zug[1]*normz[3],
                3: zug[1]*normz[2] - zug[2]*normz[1]}
            hh = h[1]*h[1] + h[2]*h[2] + h[3]*h[3]
            hn = sqrt(hh)
            p_dist2 = p[1]*p[1] + p[2]*p[2] + p[3]*p[3]
            target_pre = sqrt(p[1]*p[1] + p[2]*p[2] + p[3]*p[3] - hh)
            target = target_pre - distz
            
            h_diff[1][1] =  zug[2]*normz_diffx[3] - Mp_diffx[2]*normz[3] - zug[3]*normz_diffx[2] + Mp_diffx[3]*normz[2] 
            h_diff[1][2] =  zug[3]*normz_diffx[1] - Mp_diffx[3]*normz[1] - zug[1]*normz_diffx[3] + Mp_diffx[1]*normz[3]
            h_diff[1][3] =  zug[1]*normz_diffx[2] - Mp_diffx[1]*normz[2] - zug[2]*normz_diffx[1] + Mp_diffx[2]*normz[1] 

            h_diff[2][1] =  zug[2]*normz_diffy[3] - Mp_diffy[2]*normz[3] - zug[3]*normz_diffy[2] + Mp_diffy[3]*normz[2] 
            h_diff[2][2] =  zug[3]*normz_diffy[1] - Mp_diffy[3]*normz[1] - zug[1]*normz_diffy[3] + Mp_diffy[1]*normz[3]
            h_diff[2][3] =  zug[1]*normz_diffy[2] - Mp_diffy[1]*normz[2] - zug[2]*normz_diffy[1] + Mp_diffy[2]*normz[1] 

            h_diff[3][1] =  zug[2]*normz_diffz[3] - Mp_diffz[2]*normz[3] - zug[3]*normz_diffz[2] + Mp_diffz[3]*normz[2] 
            h_diff[3][2] =  zug[3]*normz_diffz[1] - Mp_diffz[3]*normz[1] - zug[1]*normz_diffz[3] + Mp_diffz[1]*normz[3]
            h_diff[3][3] =  zug[1]*normz_diffz[2] - Mp_diffz[1]*normz[2] - zug[2]*normz_diffz[1] + Mp_diffz[2]*normz[1] 
            
            #hn[i] = {1:h[i][1] / hh[i], 2:h[i][2] / hh[i], 3:h[i][3] / hh[i]}
            hh_diff[1] = 2*h[1]*h_diff[1][1] + 2*h[2]*h_diff[1][2] + 2*h[3]*h_diff[1][3]
            hh_diff[2] = 2*h[1]*h_diff[2][1] + 2*h[2]*h_diff[2][2] + 2*h[3]*h_diff[2][3]
            hh_diff[3] = 2*h[1]*h_diff[3][1] + 2*h[2]*h_diff[3][2] + 2*h[3]*h_diff[3][3]

            hn_diff = {1: 0.5 * hh_diff[1] / hn, 2: 0.5 * hh_diff[2] / hn, 3: 0.5 * hh_diff[3] / hn}
            
            target_diff[1] = - 0.5 * hh_diff[1] / target_pre
            target_diff[2] = - 0.5 * hh_diff[2] / target_pre
            target_diff[3] = - 0.5 * hh_diff[3] / target_pre
            
            self.isCalculated = True
                
            if 1 == self.verbose:
                # nomenklatura for wxmaxima
                print ("load(vect);")
                print ("define (Ax(w), matrix([1,0,0],[0,cos(w[1]),-sin(w[1])],[0,sin(w[1]),cos(w[1])]));")
                print ("define (Ay(w), matrix([cos(w[2]),0,-sin(w[2])],[0,1,0],[sin(w[2]),0,cos(w[2])]));")
                print ("define (Az(w), matrix([cos(w[3]),-sin(w[3]),0],[sin(w[3]),cos(w[3]),0],[0,0,1]));")
                print ("define (M(w), Az(w).Ay(w).Ax(w));")
                print ("define(V(v),matrix([v[1],v[2],v[3]]));")
                print ("define(Mp(w,v), M(w).V(v));")
                print ("define(DistZ(w,v), sqrt(Mp(w,v).Mp(w,v)));")
                print ("define(NormZ(w,v), Mp(w,v)/DistZ(w,v));")

                print ("define(Mp_diffx(w,v), diff(Mp(w,v),w[1]));")
                print ("define(Mp_diffy(w,v), diff(Mp(w,v),w[2]));")
                print ("define(Mp_diffz(w,v), diff(Mp(w,v),w[3]));")

                print ("define(DistZ_diffx(w,v), diff(DistZ(w,v),w[1]));")
                print ("define(DistZ_diffy(w,v), diff(DistZ(w,v),w[2]));")
                print ("define(DistZ_diffz(w,v), diff(DistZ(w,v),w[3]));")

                print ("define(NormZ_diffx(w,v), diff(NormZ(w,v),w[1]));")
                print ("define(NormZ_diffy(w,v), diff(NormZ(w,v),w[2]));")
                print ("define(NormZ_diffz(w,v), diff(NormZ(w,v),w[3]));")
                
                print ("P:[" + str(p[1]) + "," + str(p[2]) + "," + str(p[3]) + "];")
                print ("define(PDist(w,v), P.P);")
                print ("define(Zug(w,v), P - Mp(w,v));")
                print ("define(h(w,v), express(list_matrix_entries(Zug(w,v)) ~ list_matrix_entries(NormZ(w,v))));")
                print ("define(hh(w,v), h(w,v).h(w,v));")
                print ("define(hn(w,v), sqrt(hh(w,v)));")
                print ("define(Target(w,v), sqrt(PDist(w,v) - hh(w,v)) - DistZ(w,v));")
                print ("define(h_diffx(w,v), diff(h(w,v),w[1]));")
                print ("define(h_diffy(w,v), diff(h(w,v),w[2]));")
                print ("define(h_diffz(w,v), diff(h(w,v),w[3]));")
                print ("define(hh_diffx(w,v), diff(hh(w,v),w[1]));")
                print ("define(hh_diffy(w,v), diff(hh(w,v),w[2]));")
                print ("define(hh_diffz(w,v), diff(hh(w,v),w[3]));")
                print ("define(hn_diffx(w,v), diff(hn(w,v),w[1]));")
                print ("define(hn_diffy(w,v), diff(hn(w,v),w[2]));")
                print ("define(hn_diffz(w,v), diff(hn(w,v),w[3]));")
                print ("define(Target_diffx(w,v), diff(Target(w,v),w[1]));")
                print ("define(Target_diffy(w,v), diff(Target(w,v),w[2]));")
                print ("define(Target_diffz(w,v), diff(Target(w,v),w[3]));")
                
                print()
                arg = '[' + str(w[1]) +  ',' +  str(w[2]) + ',' +  str(w[3]) +'],[' + str(v[1]) + ',' +  str(v[2]) + ',' + str(v[3]) + ']'
                print("Mp(" + arg + ") = ", vp)
                print("Mp_diffx(" + arg + ") = ", Mp_diffx)
                print("Mp_diffy(" + arg + ") = ", Mp_diffy)
                print("Mp_diffz(" + arg + ") = ", Mp_diffz)
                print("DistZ(" + arg + ") = ", distz)
                print("NormZ(" + arg + ") = ", normz)
                print("PDist(" + arg + ") = ", p_dist2)
                
                print("DistZ_diffx(" + arg + ") = ", 0)
                print("DistZ_diffy(" + arg + ") = ", 0)
                print("DistZ_diffz(" + arg + ") = ", 0)
                
                print("NormZ_diffx(" + arg + ") = ", normz_diffx)
                print("NormZ_diffy(" + arg + ") = ", normz_diffy)
                print("NormZ_diffz(" + arg + ") = ", normz_diffz)
                
                print ("Zug(" + arg + ")", zug)
                print ("h(" + arg + ")", h)
                print ("hh(" + arg + ")", hh)
                print ("hn(" + arg + ")", hn)
                print ("Target(" + arg + ")", target)
                print ("h_diffx(" + arg + ")", h_diff[1])
                print ("h_diffy(" + arg + ")", h_diff[2])
                print ("h_diffz(" + arg + ")", h_diff[3])
                print ("hh_diffx(" + arg + ")", hh_diff[1])
                print ("hh_diffy(" + arg + ")", hh_diff[2])
                print ("hh_diffz(" + arg + ")", hh_diff[3])
                print ("hn_diffx(" + arg + ")", hn_diff[1])
                print ("hn_diffy(" + arg + ")", hn_diff[2])
                print ("hn_diffz(" + arg + ")", hn_diff[3])
                print ("Target_diffx(" + arg + ")", target_diff[1])
                print ("Target_diffy(" + arg + ")", target_diff[2])
                print ("Target_diffz(" + arg + ")", target_diff[3])

    
#a1 = point({1:1, 2:1, 3:0})
#a2 = point({1:1, 2:-1, 3:0})
a1 = point({1:1.1, 2:1.3, 3:0.7})
#a2 = point({1:1, 2:0, 3:-1})
a1 = point({1:-0.4999999403953552, 2:0.0, 3:-0.9999999701976776})

#t = trajectory({1:1.0, 2:0.2, 3:0.1})
t = trajectory({1:-0.49809741973876953, 2:-5.855072870986078e-09, 3:0.043577879667282104})

t.setOffset({1:0.0, 2:0.0, 3:0.0})
t.setTrajectoryPoint(a1)

w = {1:0.0 , 2:0.0 , 3: 0.0}

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



       
