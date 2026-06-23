import os
import sys
import htmlTools
import olex
import olexex
import olx
import gui
import shutil
from constants import *
import subprocess
import numpy as np
from helper_functions import *
from constants import *

#sys.path.insert(0, os.path.dirname(__file__))


def octadist_calc(polyhedron=test_Mn1_polyhedra):
    zeta = calc_zeta(polyhedron)
    #sigma = 'S_placeholder'
    #theta = 'T_placeholder'

    return zeta #, sigma, theta

def calc_zeta(polyhedron):
    """
    Calculate the zeta value for the Octahedron
    :returns: zeta value (float)
    """
    # Gets the central atom from the octahedron.
    # By default, Build poly will always have the central atom in the first position of the array
    # xyz are stored as strings. This divides the strings and makes a np array
    centre_xyz = np.array(polyhedron[0][1].split(' '), dtype=float)
    ligands_xyz = [np.array(np.array(xyz.split(' ')), dtype=float) for name, xyz in polyhedron[1:]]

    distances = [np.linalg.norm((xyz - centre_xyz)) for xyz in ligands_xyz]
    print(f'Distances: {distances}')
    mean_bond_distance = np.mean(distances)
    deviations = [np.linalg.norm(np.abs(d - mean_bond_distance)) for d in distances]
    zeta = np.mean(deviations)
    print(f'Zeta: {zeta}')
    return zeta





