#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 12:04:14 2020

@author: joelherreravazquez
"""

import numpy as np

import Kraken as kn

##############################################################    
P_Obj = kn.surf()
P_Obj.Rc = 0.0
P_Obj.Thickness = 0
P_Obj.Glass = "AIR"
P_Obj.Diameter = 30.0

P_Obj2 = kn.surf()
P_Obj2.Rc = 0.0
P_Obj2.Thickness = 10
P_Obj2.Glass = "AIR"
P_Obj2.Diameter = 100.0

L1a = kn.surf()
L1a.Rc = 9.284706570002484E+001
L1a.Thickness = 6.0
L1a.Glass = "BK7"
L1a.Diameter = 30.0
L1a.Axicon = 0

L1b = kn.surf()
L1b.Rc = -3.071608670000159E+001

L1b.Thickness = 3.0
L1b.Glass = "F2"
L1b.Diameter = 30

L1c = kn.surf()
L1c.Rc = -7.819730726078505E+001
L1c.Thickness = 9.737604742910693E+001
L1c.Glass = "AIR"
L1c.Diameter = 30

P_Ima = kn.surf()
P_Ima.Rc = 0.0
P_Ima.Thickness = 0.0
P_Ima.Glass = "MIRROR"
P_Ima.Diameter = 30.0
P_Ima.Name = "Plano imagen"
P_Ima.DespZ = 10
P_Ima.TiltX = 6.

A = [P_Obj, P_Obj2, L1a, L1b, L1c, P_Ima]

######################


configuracion_1 = kn.Kraken_setup()

Doblete = kn.system(A, configuracion_1)
Rayos = kn.raykeeper(Doblete)

tam = 10
rad = 14.0
tsis = len(A) - 1

for nsc in range(0, 100):
    for j in range(-tam, tam + 1):
        # for i in range(-tam,tam+1):

        x_0 = (0 / tam) * rad
        y_0 = (j / tam) * rad
        r = np.sqrt((x_0 * x_0) + (y_0 * y_0))
        if r < rad:
            tet = 0.0
            pSource_0 = [x_0, y_0, 0.0]
            dCos = [0.0, np.sin(np.deg2rad(tet)), np.cos(np.deg2rad(tet))]

            W = 0.4
            Doblete.NsTrace(pSource_0, dCos, W)
            Rayos.push()

kn.display2d(Doblete, Rayos, 0)

# X,Y,Z,L,M,N=Rayos.pick(2)
# plt.plot(L,M, 'ro')

# X,Y,Z,L,M,N=Rayos.pick(1)
# plt.plot(X,Y, 'x')

# # axis labeling
# plt.xlabel('numbers')
# plt.ylabel('values')

# # figure name
# plt.title('Dot Plot : Red Dots')
# plt.show()
