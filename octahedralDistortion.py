import os
import htmlTools
import olex
import olexex
import olx
import gui
import shutil
from constants import *
import subprocess
import numpy as np
from SymmetryMeasurements import *
from helper_functions import *
from constants import *

def auto_octadist():
    sel = olex.f('sel()') # Gets the selection
    if sel != '':
        label = sel.split(' ')
        poly = build_polyhedra_from_centre(label)


        return True
    else:
        return False

def octadist(polyhedron=test_Mn1_polyhedra):
    if len(polyhedron) != 7:
        print('Invalid polyhedra: central atom has more than six connected atoms.')

    mean_d = calc_mean_bond_distance(polyhedron)
    print(mean_d)
    return mean_d

def calc_mean_bond_distance(polyhedron):
    centre_label = polyhedron[0][0]
    centre_xyz = np.array(polyhedron[0][1].split(' '))
    distances = [np.linalg.norm(np.array(np.array(xyz.split(' '))) - centre_xyz) for name, xyz in polyhedron[1:]]
    return np.mean(distances)





