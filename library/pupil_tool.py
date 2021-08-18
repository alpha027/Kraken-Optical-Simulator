# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 17:16:17 2021

@author: JOELHERRERAVAZQUEZ
"""

##############################################################################

import numpy as np
from raykeeper import *
from display import *

import scipy
from scipy import optimize
from scipy.optimize import fmin_cg

from scipy.optimize import fsolve
from AstroAtmosphere import *


##############################################################################

def RMS_Pupil(r, SYSTEM, sup, W):
    SYSTEM.TargSurf(sup)
    SYSTEM.IgnoreVignetting(0)
    SYSTEM.SurfFlat(sup, 0)

    RP = raykeeper(SYSTEM)
    tet = 0.1

    ######################################################################

    s_0 = [0.0, 0.0, 0.0]
    c_0 = [0.0, 0.0, 1.0]
    SYSTEM.Trace(s_0, c_0, W)
    RP.push()

    c_1 = [np.sin(np.deg2rad(tet)), 0.0, np.cos(np.deg2rad(tet))]
    s_0 = [r, 0.0, 0.0]
    SYSTEM.Trace(s_0, c_1, W)
    RP.push()

    c_2 = [np.sin(np.deg2rad(-tet)), 0.0, np.cos(np.deg2rad(-tet))]
    s_0 = [-r, 0.0, 0.0]
    SYSTEM.Trace(s_0, c_2, W)
    RP.push()

    c_3 = [0.0, np.sin(np.deg2rad(tet)), np.cos(np.deg2rad(tet))]
    s_0 = [0.0, r, 0.0]
    SYSTEM.Trace(s_0, c_3, W)
    RP.push()

    c_4 = [0.0, np.sin(np.deg2rad(-tet)), np.cos(np.deg2rad(-tet))]
    s_0 = [0.0, -r, 0.0]
    SYSTEM.Trace(s_0, c_4, W)
    RP.push()

    X, Y, Z, L, M, N = RP.pick(sup)

    delta_Z = 0
    X = ((L / N) * delta_Z) + X
    Y = ((M / N) * delta_Z) + Y

    cenX = np.mean(X)
    cenY = np.mean(Y)

    x1 = X - cenX
    y1 = Y - cenY

    R2 = ((x1 * x1) + (y1 * y1))
    R_RMS = np.sqrt(np.mean(R2))

    SYSTEM.SurfFlat(-1)
    SYSTEM.TargSurf(-1)
    SYSTEM.Vignetting(0)
    RP.clean()
    return R_RMS


######################################################################


def R_RMS(delta_Z, L, M, N, X, Y):
    X = ((L / N) * delta_Z) + X
    Y = ((M / N) * delta_Z) + Y

    cenX = np.mean(X)
    cenY = np.mean(Y)

    x1 = X - cenX
    y1 = Y - cenY

    R2 = ((x1 * x1) + (y1 * y1))
    R_RMS = np.sqrt(np.mean(R2))
    return R_RMS


##############################################################################

def FuncVectorCross(Z1, XYZa, LMNa, XYZb, LMNb, xy):
    [La, Ma, Na] = LMNa
    [X0a, Y0a, Z0a] = XYZa
    [Lb, Mb, Nb] = LMNb
    [X0b, Y0b, Z0b] = XYZb

    if xy == 0:
        V = ((La / Na) * (Z1 - Z0a) + X0a) - ((Lb / Nb) * (Z1 - Z0b) + X0b)
    else:
        V = ((Ma / Na) * (Z1 - Z0a) + Y0a) - ((Mb / Nb) * (Z1 - Z0b) + Y0b)

    return V


##############################################################################

def DerVectCross(Z1, XYZa, LMNa, XYZb, LMNb, xy):
    h = 0.0000001
    f1 = FuncVectorCross(Z1 + h, XYZa, LMNa, XYZb, LMNb, xy)
    f2 = FuncVectorCross(Z1 - h, XYZa, LMNa, XYZb, LMNb, xy)
    der = (f1 - f2) / (2 * h)
    return der


##############################################################################

def SolveVectCross(XYZa, LMNa, XYZb, LMNb, xy):
    [La, Ma, Na] = LMNa
    [X0a, Y0a, Z0a] = XYZa
    [Lb, Mb, Nb] = LMNb
    [X0b, Y0b, Z0b] = XYZb

    # if np.abs(La) > np.abs(Ma) or np.abs(Lb) > np.abs(Mb):
    #     xy=0
    # else:
    #     xy=1

    Z1 = 0.0000001
    cnt = 0

    while True:
        fun = FuncVectorCross(Z1, XYZa, LMNa, XYZb, LMNb, xy)
        derfun = DerVectCross(Z1, XYZa, LMNa, XYZb, LMNb, xy)

        Z2 = Z1 - (fun / derfun)

        if np.abs(Z1 - Z2) < 0.000001:  # si la distancia entre raiz y funcion es de 0.001micras
            break
        else:
            Z1 = Z2
        if cnt == 5:
            break
        cnt = cnt + 1

    X2 = (La / Na) * (Z2 - Z0a) + X0a
    Y2 = (Ma / Na) * (Z2 - Z0a) + Y0a

    return [X2, Y2, Z2]


##############################################################################

def DerFpupil(SYSTEM, XY, H, sup, tet, W, xy):
    h = 0.0000001
    der = Fpupil(SYSTEM, XY + h, H, sup, tet, W, xy) - Fpupil(SYSTEM, XY - h, H, sup, tet, W, xy)
    DER = der / (2.0 * h)
    return DER


##############################################################################

def Fpupil(SYSTEM, XY, H, sup, tet, W, xy):
    if xy == 0:
        pSource_0 = [XY, 0.0, 0.0]
        dCos = [np.sin(np.deg2rad(tet)), 0.0, np.cos(np.deg2rad(tet))]
    else:
        pSource_0 = [0.0, XY, 0.0]
        dCos = [0.0, np.sin(np.deg2rad(tet)), np.cos(np.deg2rad(tet))]

    SYSTEM.Trace(pSource_0, dCos, W)

    s = np.asarray(SYSTEM.SURFACE)
    a = np.squeeze(np.argwhere(s == sup))
    [X2, Y2, Z2] = SYSTEM.OST_XYZ[a]

    if xy == 0:
        R = X2 - H
    else:
        R = Y2 - H

    return R


#######################################################################

def SolveRayPupil(SYSTEM, H, tet, W, sup, xy):
    XY0 = 0.0000001
    cnt = 0

    while True:
        XY1 = XY0 - (Fpupil(SYSTEM, XY0, H, sup, tet, W, xy) / DerFpupil(SYSTEM, XY0, H, sup, tet, W, xy))
        if np.abs(XY0 - XY1) < 0.000001:  # si la distancia entre raiz y funcion es de 0.001micras
            break
        else:
            XY0 = XY1
        if cnt == 5:
            break
        cnt = cnt + 1

    if xy == 0:
        pSource_0 = [XY0, 0.0, 0.0]
        dCos = [np.sin(np.deg2rad(tet)), 0.0, np.cos(np.deg2rad(tet))]
    else:
        pSource_0 = [0.0, XY0, 0.0]
        dCos = [0.0, np.sin(np.deg2rad(tet)), np.cos(np.deg2rad(tet))]

    return pSource_0, dCos

    ##############################################################


class pupilcalc:
    def __init__(self, SYSTEM, sup, W, ApTyp="EPD", AV=1.0):
        if AV == 0:
            print("ERROR: Aperture cannot be set equal to zero, default value will be used (1.0)")
            AV = 1.0
        if ApTyp == "STOP":
            print("Note: STOP surface has been selected, entrance aperture is calculated with STOP diameter")

        # print("kajshskajdhkajdhkajhdskjahskdjhaksjdhkajshkdjahkjsh")
        # print(" pupil2 is in tha house")
        self.FieldType = "angle"  # "height"
        self.ApertureType = ApTyp
        self.ApertureValue = AV
        self.x0 = 0
        self.y0 = 0
        self.z0 = 0
        self.L = 0.
        self.M = 0.
        self.N = 1.
        self.Cordx = np.asarray(0)
        self.Cordy = np.asarray(0)
        self.Ptype = "hexapolar"
        self.Samp = 6
        self.FieldX = 0.
        self.FieldY = 0.
        self.DirPupSal = [0.0, 0.0, 0.0]
        self.rad = 0
        self.teta = 0
        self.PupilInpFactor = 0.99
        self.menter = 1.0
        
        
        
        self.AtmosRef=0
        self.T   = 283.15    # k
        self.P   = 100500    # Pa
        self.H   = 0.0       # ratio 1 to 0
        self.xc  = 450       # ppm
        self.lat = 50    # degrees
        self.h   = 0      # m
        self.l1  = 5000.60169      # micron
        self.l2  = 0.50169      # micron
        self.z0  = 75.0

        # EPD Entrance pupil diameter
        # STP defined by stop diameter
        # F/# F number
        # NA numeric apperture
        # CA Cone angle

        delta_Z = 0
        r = 0.000001
        cnt = 0

        while True:
            fun = RMS_Pupil(r, SYSTEM, sup, W)
            h = 0.0000001
            f1 = RMS_Pupil(r + h, SYSTEM, sup, W)
            f2 = RMS_Pupil(r - h, SYSTEM, sup, W)
            der = (f1 - f2) / (2 * h)

            r2 = r - (fun / der)

            if np.abs(r - r2) < 0.0000000001:  # si la distancia entre raiz y funcion es de 0.001micras
                break
            else:
                r = r2

            if cnt == 5:
                break
            cnt = cnt + 1

        SYSTEM.IgnoreVignetting(0)

        RP = raykeeper(SYSTEM)
        tet = 0.1

        ######################################################################

        s_0 = [0.0, 0.0, 0.0]

        c_0 = [0.0, 0.0, 1.0]
        SYSTEM.Trace(s_0, c_0, W)
        RP.push()

        c_1 = [np.sin(np.deg2rad(tet)), 0.0, np.cos(np.deg2rad(tet))]
        s_0 = [r, 0.0, 0.0]
        SYSTEM.Trace(s_0, c_1, W)
        RP.push()

        c_2 = [np.sin(np.deg2rad(-tet)), 0.0, np.cos(np.deg2rad(-tet))]
        s_0 = [-r, 0.0, 0.0]
        SYSTEM.Trace(s_0, c_2, W)
        RP.push()

        c_3 = [0.0, np.sin(np.deg2rad(tet)), np.cos(np.deg2rad(tet))]
        s_0 = [0.0, r, 0.0]
        SYSTEM.Trace(s_0, c_3, W)
        RP.push()

        c_4 = [0.0, np.sin(np.deg2rad(-tet)), np.cos(np.deg2rad(-tet))]
        s_0 = [0.0, -r, 0.0]
        SYSTEM.Trace(s_0, c_4, W)
        RP.push()

        """ Angulos en las superficies, para sacar la amplificacion de la pupila """

        X, Y, Z, L, M, N = RP.pick(0)
        teta = 0
        for s in range(1, 5):
            teta = teta + np.rad2deg(np.arccos(L[0] * L[s] + M[0] * M[s] + N[0] * N[s]))
        tetaIni = np.abs(teta / 4.0)
        # print(tetaIni, " Angulo")

        X, Y, Z, L, M, N = RP.pick(sup)
        teta = 0
        for s in range(1, 5):
            teta = teta + np.rad2deg(np.arccos(L[0] * L[s] + M[0] * M[s] + N[0] * N[s]))
        tetaSup = np.abs(teta / 4.0)
        # print(tetaSup, " Angulo")

        X, Y, Z, L, M, N = RP.pick(-1)
        teta = 0
        for s in range(1, 5):
            teta = teta + np.rad2deg(np.arccos(L[0] * L[s] + M[0] * M[s] + N[0] * N[s]))
        tetaEnd = np.abs(teta / 4.0)
        # print(tetaEnd, " Angulo")

        M_ENTER_P = tetaIni / tetaSup
        # print("Amplificación pupila de entrada respecto al STOP: ", M_ENTER_P)
        M_EXIT_P = tetaIni / tetaEnd
        # print("Amplificación pupila de entrada respecto a pupila de entrada: ", M_EXIT_P)

        ##############################################################

        """ Tamanio del system STOP """

        STOP_DIAM = SYSTEM.SDT[sup].Diameter
        # print("Tamanio del STOP: ", STOP_DIAM)

        if self.ApertureType == "EPD":
            D_Input_Pup = self.ApertureValue

        if self.ApertureType == "STOP":
            D_Input_Pup = STOP_DIAM / M_ENTER_P

        RadPupInp = D_Input_Pup / 2.0
        D_Exit_Pup = STOP_DIAM * M_EXIT_P
        RadPupOut = D_Exit_Pup / 2.0

        # print("Enter pupil diameter: ", D_Input_Pup)
        # print("Exit pupil diameter: ", D_Exit_Pup)

        """Posicion e la pupila de entrada y de salida"""

        Xs, Ys, Zs, Ls, Ms, Ns = RP.pick(0)
        Xe, Ye, Ze, Le, Me, Ne = RP.pick(-1)

        delta_Z = 0

        ZZ = Ls, Ms, Ns, Xs, Ys
        # noinspection PyTypeChecker
        v0 = scipy.optimize.fsolve(R_RMS, delta_Z, args=ZZ)

        ZZ = Le, Me, Ne, Xe, Ye
        # noinspection PyTypeChecker
        vf = scipy.optimize.fsolve(R_RMS, delta_Z, args=ZZ)

        # print("Enter pupil Position: ",v0)
        PosPupInp = np.asarray([0, 0, v0[0]])

        """-----------------------------------------------"""
        # print("Orientacion pupila de salida")
        OPS = np.asarray([Le[0], Me[0], Ne[0]])
        DirPupSal = OPS
        # print(OPS)

        """------------------------------------------------"""

        X, Y, Z, L, M, N = RP.pick(-1)

        px = ((L[0] / N[0]) * vf) + X[0]
        py = ((M[0] / N[0]) * vf) + Y[0]

        # X, Y, Z, L, M, N = RP.pick(-1)

        pz = vf

        # print(" Exit pupil Position: ",vf)
        PosPupOut = np.asarray([px[0], py[0], vf[0] + Ze[0]])

        PosPupOutFoc = np.asarray([px[0], py[0], pz[0]])
        # print("Exit pupil coordinates from image plane: ", px, py, pz)

        # kn.display2d(SYSTEM,RP,0)
        # kn.display2d(SYSTEM,RP,1)

        SYSTEM.Vignetting(0)
        RP.clean()

        self.RadPupInp = RadPupInp
        self.PosPupInp = PosPupInp
        self.RadPupOut = RadPupOut
        self.PosPupOut = PosPupOut
        self.PosPupOutFoc = PosPupOutFoc
        self.DirPupSal = DirPupSal
        self.menter = M_ENTER_P

        # return RadPupInp, PosPupInp, RadPupOut, PosPupOut, PosPupOutFoc

    def __patern_rect(self, x, y, kx, ky):
        for i in range(-(self.Samp * kx), (kx * self.Samp) + 1):
            for j in range(-(self.Samp * ky), (ky * self.Samp) + 1):

                x_0 = (i / self.Samp)
                y_0 = (j / self.Samp)
                r = np.sqrt((x_0 * x_0) + (y_0 * y_0))

                if r <= 1.0:
                    x.append(x_0)
                    y.append(y_0)
                    # print(x)
        # print(y)

        return x, y

    def Pattern(self):

        self.Samp = int(self.Samp)
        x = []
        y = []

        if self.Ptype == "rteta":
            x.append(self.rad * np.cos(np.deg2rad(self.teta)))
            y.append(self.rad * np.sin(np.deg2rad(self.teta)))

        if self.Ptype == "chief":
            x.append(0.0)
            y.append(0.0)

        if self.Ptype == "hexapolar":
            x.append(0.0)
            y.append(0.0)
            for j in range(1, self.Samp + 1):
                m = 1.0 / self.Samp
                r = m * j
                k = j * 6
                ang = 360.0 / k
                for h in range(0, k):
                    # print(r, j*6, h*ang)
                    x.append(r * np.cos(np.deg2rad(h * ang)))
                    y.append(r * np.sin(np.deg2rad(h * ang)))

        if self.Ptype == "square":
            x, y = self.__patern_rect(x, y, 1, 1)

        if self.Ptype == "fanx":
            x, y = self.__patern_rect(x, y, 1, 0)

        if self.Ptype == "fany":
            x, y = self.__patern_rect(x, y, 0, 1)

        if self.Ptype == "fan":
            x, y = self.__patern_rect(x, y, 1, 0)
            x, y = self.__patern_rect(x, y, 0, 1)

        if self.Ptype == "rand":
            p = 1000000.0
            self.Sample = 4 * self.Samp * self.Samp
            x_i = np.random.randint(-p, p, self.Sample) / p
            y_i = np.random.randint(-p, p, self.Sample) / p
            for i in range(0, self.Sample):
                x_0 = x_i[i]
                y_0 = y_i[i]
                r = np.sqrt((x_0 * x_0) + (y_0 * y_0))
                if r < 1.0:
                    x.append(x_0)
                    y.append(y_0)

        self.Cordx = np.asarray(x)
        self.Cordy = np.asarray(y)

    def Pattern2Field(self):

        self.Pattern()

        x = self.Cordx * self.RadPupInp
        y = self.Cordy * self.RadPupInp

        # x=x*self.RadPupInp
        # y=y*self.RadPupInp

        Px, Py, Pz = self.PosPupInp

        if self.FieldType == "angle":
            if self.AtmosRef==1:
                
                # Parameters at Cerro Armazones
                T   = self.T
                P   = self.P
                H   = self.H
                xc  = self.xc
                lat = self.lat
                h   = self.h
                l1  = self.l1
                l2  = self.l2
                z0  = self.z0
                    
                # Initializing dispersion model
                at  = Observatory()
                
                # Calculating indices of refraction for l1 and l2
                n1  = at.n_tph(l=l1, T=T, p=P, RH=H, xc=xc)
                n2  = at.n_tph(l=l2, T=T, p=P, RH=H, xc=xc)
                
                
                # Density of the atmosphere (following CIPM-81/91 equations)
                rho = at.rho(p=P, T=T, RH=H, xc=xc)
                
                # Initializing refraction model and setting the reduced height
                disp = dispersion(lat, h)
                disp.setReducedHeight(P, rho)
                
                
                        
                f_x = z0 + self.FieldX    
                f_y = self.FieldY    
                
                Z0=np.sqrt((f_x**2)+(f_y**2))    
                # Calculation of the atmopheric dipsersion
                atm_dispersion = disp.cassini(n1, n2, Z0)
                # print ('The dispersion is %.03f milli arc seconds' %(atm_dispersion), l2)            
                        
            
                teta = np.arctan2(f_x, f_y)
                
                tx = self.FieldX  + (atm_dispersion * np.sin(teta))
                ty = self.FieldY  + (atm_dispersion * np.cos(teta))
                
                shiftX = Pz * np.sin(np.deg2rad(-tx))
                shiftY = Pz * np.sin(np.deg2rad(-ty))
                
            else:
            
                shiftX = Pz * np.sin(np.deg2rad(-self.FieldX))
                shiftY = Pz * np.sin(np.deg2rad(-self.FieldY))
            
            f_type = 1.
        else:
            shiftX = -self.FieldX
            shiftY = -self.FieldY
            f_type = 0.

        x0 = np.copy(x * f_type) + shiftX
        y0 = np.copy(y * f_type) + shiftY

        z = np.ones_like(x) * Pz
        z0 = np.zeros_like(x)

        X2 = (x - x0) * (x - x0)
        Y2 = (y - y0) * (y - y0)
        Z2 = (z - z0) * (z - z0)

        S = np.sqrt(X2 + Y2 + Z2)
        L = (x - x0) / S
        M = (y - y0) / S
        N = (z - z0) / S

        return x0, y0, z0, L, M, N
