#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Examp Doublet Lens Pupil Seidel"""

import Kraken as kn
import numpy as np

#_________________________________________#
   
P_Obj = kn.surf()
P_Obj.Rc = 0.0
P_Obj.Thickness = 100
P_Obj.Glass = "AIR"
P_Obj.Diameter = 30.0
P_Obj.Name = "P Obj"

#_________________________________________#

L1a = kn.surf()
L1a.Rc = 9.284706570002484E+001
L1a.Thickness = 6.0
L1a.Glass = "N-BK7"
L1a.Diameter = 30.0
L1a.Axicon = 0

#_________________________________________#

L1b = kn.surf()
L1b.Rc = -3.071608670000159E+001
L1b.Thickness = 3.0
L1b.Glass = "F2"
L1b.Diameter = 30

#_________________________________________#

L1c = kn.surf()
L1c.Rc = -7.819730726078505E+001
L1c.Thickness = 9.737604742910693E+001 - 40
L1c.Glass = "AIR"
L1c.Diameter = 30

#_________________________________________#

pupila = kn.surf()
pupila.Rc = 0
pupila.Thickness = 40.
pupila.Glass = "AIR"
pupila.Diameter = 15.0
pupila.Name = "Ap Stop"

#_________________________________________#

P_Ima = kn.surf()
P_Ima.Rc = 0.0
P_Ima.Thickness = 0.0
P_Ima.Glass = "AIR"
P_Ima.Diameter = 20.0
P_Ima.Name = "Plano imagen"

#_________________________________________#

A = [P_Obj, L1a, L1b, L1c, pupila, P_Ima]
config_1 = kn.Kraken_setup()

#_________________________________________#

Doblete = kn.system(A, config_1)

#_________________________________________#

W = 0.6
sup = 4
AperVal = 3
AperType = "EPD"
field = 3.25
fieldType = "angle"

#_________________________________________#

AB = kn.Seidel(Doblete, sup, W, AperType, AperVal, field, fieldType)
print( AB[0][0])
print(np.sum(AB[1][0]), np.sum(AB[1][1]), np.sum(AB[1][2]), np.sum(AB[1][3]), np.sum(AB[1][4]))

j=1
print( AB[0][0+j])
print(np.sum(AB[1+j][0]), np.sum(AB[1+j][1]), np.sum(AB[1+j][2]), np.sum(AB[1+j][3]), np.sum(AB[1+j][4]))

j=2
print( AB[0][0+j])
print(np.sum(AB[1+j][0]), np.sum(AB[1+j][1]), np.sum(AB[1+j][2]), np.sum(AB[1+j][3]), np.sum(AB[1+j][4]))

j=3
print( AB[0][0+j])
print(np.sum(AB[1+j][0]), np.sum(AB[1+j][1]), np.sum(AB[1+j][2]), np.sum(AB[1+j][3]), np.sum(AB[1+j][4]))

#_________________________________________#

Pup = kn.pupilcalc(Doblete, sup, W, AperType, AperVal)
Pup.Samp = 25
Pup.Ptype = "fan"
Pup.FieldY = field
x, y, z, L, M, N = Pup.Pattern2Field()
Rayos = kn.raykeeper(Doblete)

#_________________________________________#

for i in range(0, len(x)):
    pSource_0 = [x[i], y[i], z[i]]
    dCos = [L[i], M[i], N[i]]
    Doblete.Trace(pSource_0, dCos, W)
    Rayos.push()

#_________________________________________#

kn.display2d(Doblete, Rayos, 0)