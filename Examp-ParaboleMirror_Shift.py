#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Examp Parabole Mirror Shift"""

import numpy as np
import Kraken as kn

# ______________________________________#

P_Obj = kn.surf()
P_Obj.Thickness = 1000.0
P_Obj.Diameter = 300
P_Obj.Drawing = 0

# ______________________________________#

M1 = kn.surf()
M1.Rc = -2000.0
M1.Thickness = M1.Rc / 2
M1.k = -1.0
M1.Glass = "MIRROR"
M1.Diameter = 300
M1.ShiftY = 200

# ______________________________________#

P_Ima = kn.surf()
P_Ima.Glass = "AIR"
P_Ima.Diameter = 1600.0
P_Ima.Drawing = 0
P_Ima.Name = "Plano imagen"

# ______________________________________#

A = [P_Obj, M1, P_Ima]
configuracion_1 = kn.Kraken_setup()

# ______________________________________#

Espejo = kn.system(A, configuracion_1)
Rayos = kn.raykeeper(Espejo)

# ______________________________________#

tam = 5
rad = 150.0
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
            Espejo.Trace(pSource_0, dCos, W)
            Rayos.push()

# ______________________________________#

kn.display2d(Espejo, Rayos, 0)
