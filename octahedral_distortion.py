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
from scipy.spatial import ConvexHull

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



class CalcDistortion:
    def __init__(self, coords):

        points = []
        for c in coords:
            if type(c) is not np.array:
                c = np.array(c.split(' '), dtype=np.float64)
            points.append(c)

        self.coords = points # xyz Coordinates of central (first) and ligands (rest)
        self.vectors = self.calc_vectors() # Vectors pointing from metal to ligand
        self.bond_distances = self.calc_bond_distances(coords)
        self.mean_bond_distance = np.mean(self.bond_distances)

        self.angles = self.calc_all_angles() # Angles is a sorted list. The last three elements will be
        self.cis_angles = self.angles[:-3]
        self.trans_angles = self.angles[-3:]

        self.convex_hull = ConvexHull(self.coords)
        self.volume = self.convex_hull.volume

        self.zeta = self.calc_zeta()
        self.sigma = self.calc_sigma()
        self.theta = self.calc_theta()

    def calc_vectors(self):
        vs = []
        for coord in self.coords[1:]:
            v = coord - self.coords[0]
            vs.append(v)
        return np.array(vs)

    def calc_bond_distances(self, coords):
        ds = []
        for v in self.vectors:
            d = np.linalg.norm(v)
            ds.append(d)
        return np.array(ds, dtype=np.float64)

    def calc_all_angles(self):
        angles = []
        for i in range(0,6):
            for j in range(i+1,6):
                v1 = self.vectors[i] / np.linalg.norm(self.vectors[i])
                v2 = self.vectors[j] / np.linalg.norm(self.vectors[j])

                angle = np.degrees(np.arccos(np.dot(v1, v2)))
                angles.append(angle)
        angles.sort()
        return np.array(angles)


    def calc_zeta(self):
        deviations = [np.abs(d - self.mean_bond_distance) for d in self.bond_distances]
        return np.sum(deviations)


    def calc_sigma(self):
        sigma = np.sum(np.abs(90 - self.cis_angles))
        return sigma

    def calc_theta(self):
        return 12345





def print_od_results(calculation: CalcDistortion, atom_label, file):
    print('\n' + '='*70)
    print(f'Octahedral distortion parameters calculated for {atom_label} in {os.path.basename(file)}')
    print('-' * 70)
    print(f"{'Mean d(M-X)':<12}{calculation.mean_bond_distance:>12.4f}{'   '}{'Angstroms':<12}")
    print(f"{'Zeta':<12}{calculation.zeta:>12.4f}{'   '}{'Angstroms':<12}")
    print(f"{'Sigma':<12}{calculation.sigma:>12.4f}{'   '}{'Degrees':<12}")
    print(f"{'Theta':<12}{calculation.theta:>12.4f}{'   '}{'Degrees':<12}")
    print(f"{'Volume':<12}{calculation.volume:>12.4f}{'   '}{'Angstrom^3':<12}")
    print('=' * 70)