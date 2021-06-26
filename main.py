import scipy
from scipy import optimize
from scipy.optimize import fmin_cg

from scipy.optimize import fsolve

import matplotlib.pyplot as plt
import numpy as np

import os, sys

import Kraken as kn

currentDirectory = os.getcwd()
sys.path.insert(1, currentDirectory + '/library')
from PhaseCalc import Phase

if __name__ == '__main__':
    P_Obj = kn.surf()
    P_Obj.Rc = 0
    P_Obj.Thickness = 1000 + 3.452200000000000E+003
    P_Obj.Glass = "AIR"
    P_Obj.Diameter = 1.059E+003 * 2.0

    Thickness: float = 3.452200000000000E+003
    M1 = kn.surf()
    M1.Rc = -9.638000000004009E+003
    M1.Thickness = -Thickness
    M1.k = -1.077310000000000E+000
    M1.Glass = "MIRROR"
    M1.Diameter = 1.059E+003 * 2.0
    M1.InDiameter = 250 * 2.0
    M1.TiltY = 0.0
    M1.TiltX = 0.0

    M1.AxisMove = 0
    M2 = kn.surf()
    M2.Rc = -3.93E+003
    M2.Thickness = Thickness + 1037.525880
    M2.k = -4.328100000000000E+000
    M2.Glass = "MIRROR"
    M2.Diameter = 3.365E+002 * 2.0
    M2.TiltY = 0.0
    M2.TiltX = 0.0
    M2.DespY = 0.05
    M2.DespX = 0.1

    M2.AxisMove = 0

    P_Ima = kn.surf()
    P_Ima.Diameter = 300.0
    P_Ima.Glass = "AIR"
    P_Ima.Name = "Plano imagen"

    A = [P_Obj, M1, M2, P_Ima]

    ######################

    configuracion_1 = kn.Kraken_setup()
    Telescopio = kn.system(A, configuracion_1)

    W = 0.4
    sup = 1
    Samp = 10

    Ptype = "hexapolar"  # "rand" # "hexapolar"
    FieldY = 0.13
    FieldX = -0.01
    FieldType = "angle"

    AperType = "STOP"
    fieldType = "angle"
    AperVal = 2100.

    Z, X, Y, P2V = Phase(Telescopio, sup, W, AperType, AperVal, configuracion_1, Samp, Ptype, FieldY, FieldX, FieldType)
    NC = 38
    A = np.ones(NC)

    z_coeff, MatNotation, w_rms, fitt_error = kn.Zernike_Fitting(X, Y, Z, A)
    A = np.abs(z_coeff)
    Zeros = np.argwhere(A > 0.0001)
    AA = np.zeros_like(A)
    AA[Zeros] = 1
    A = AA
    z_coeff, MatNotation, w_rms, fitt_error = kn.Zernike_Fitting(X, Y, Z, A)

    print("Peak to valley: ", P2V)

    for i in range(0, NC):
        print("z ", i + 1, "  ", "{0:.6f}".format(float(z_coeff[i])), "  :  ", MatNotation[i])

    print("RMS: ", "{:.4f}".format(float(w_rms)), " Error del ajuste: ", fitt_error)
    z_coeff[0] = 0

    print("RMS to chief: ", np.sqrt(np.sum(z_coeff * z_coeff)))
    z_coeff[1] = 0
    z_coeff[2] = 0
    print("RMS to centroid: ", np.sqrt(np.sum(z_coeff * z_coeff)))

    RR = kn.raykeeper(Telescopio)

    Pup = kn.pupilcalc(Telescopio, sup, W, AperType, AperVal)

    Pup.FieldX = FieldX
    Pup.FieldY = FieldY

    x, y, z, L, M, N = Pup.Pattern2Field()

    for i in range(0, len(x)):
        pSource_0 = [x[i], y[i], z[i]]
        dCos = [L[i], M[i], N[i]]
        Telescopio.Trace(pSource_0, dCos, W)
        RR.push()

    kn.display3d(Telescopio, RR, 2)

    X, Y, Z, L, M, N = RR.pick(-1)

    plt.plot(X, Y, 'x')

    # axis labeling
    plt.xlabel('numbers')
    plt.ylabel('values')

    # figure name
    plt.title('Dot Plot : Red Dots')
    plt.axis('square')
    plt.show()
