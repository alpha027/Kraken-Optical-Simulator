#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 12:04:14 2020

@author: joelherreravazquez
"""

import Kraken as kn

import numpy as np
import matplotlib.pyplot as plt
import time

configuracion_1 = kn.Kraken_setup()

##############################################################    

P_Obj = kn.surf()
P_Obj.Rc = 0.0
P_Obj.Thickness = 1
P_Obj.Glass = "AIR"
P_Obj.Diameter = 30.0

L1a = kn.surf()
L1a.Rc = 5.513435044607768E+001
L1a.Thickness = 6.0
L1a.Glass = "BK7"
L1a.Diameter = 30.0

L1b = kn.surf()
L1b.Rc = -4.408716526030626E+001
L1b.Thickness = 3.0
L1b.Glass = "F2"
L1b.Diameter = 30

L1c = kn.surf()
L1c.Rc = -2.246906271406796E+002
L1c.Thickness = 9.737871661422000E+001
L1c.Glass = "AIR"
L1c.Diameter = 30

Z = np.zeros(36)
Z[8] = 0.5
Z[9] = 0.5
Z[10] = 0.5
Z[11] = 0.5
Z[12] = 0.5
Z[13] = 0.5
Z[14] = 0.5
Z[15] = 0.5
L1c.ZNK = Z

P_Ima = kn.surf()
P_Ima.Rc = 0.0
P_Ima.Thickness = 0.0
P_Ima.Glass = "AIR"
P_Ima.Diameter = 100.0
P_Ima.Name = "Plano imagen"

A = [P_Obj, L1a, L1b, L1c, P_Ima]

######################


Doblete = kn.system(A, configuracion_1)
Rayos = kn.raykeeper(Doblete)

tam = 5
rad = 12.0
tsis = len(A) - 1

for i in range(-tam, tam + 1):
    for j in range(-tam, tam + 1):

        x_0 = (i / tam) * rad
        y_0 = (j / tam) * rad
        r = np.sqrt((x_0 * x_0) + (y_0 * y_0))
        if r < rad:
            tet = 0.0
            pSource_0 = [x_0, y_0, 0.0]
            dCos = [0.0, np.sin(np.deg2rad(tet)), np.cos(np.deg2rad(tet))]

            W = 0.4
            Doblete.Trace(pSource_0, dCos, W)
            Rayos.push()

            # W=0.5
            # Doblete.Trace(pSource_0, dCos,W)
            # Rayos.push()

            # W=0.6
            # Doblete.Trace(pSource_0, dCos,W)
            # Rayos.push()

kn.display3d(Doblete, Rayos, 2)

kn.display2d(Doblete, Rayos, 0)
