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
from itertools import combinations

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

        self.coords = np.array(points) # xyz Coordinates of central (first) and ligands (rest)
        self.central_atom = self.coords[0]
        self.vertices = self.coords[1:]
        self.vectors = self.calc_vectors() # Vectors pointing from metal to ligand
        self.bond_distances = self.calc_bond_distances(coords)
        self.mean_bond_distance = np.mean(self.bond_distances)

        self.angles = self.calc_all_angles() # Angles is a sorted list. The last three elements will be
        self.cis_angles = self.angles[:-3]
        self.trans_angles = self.angles[-3:]

        self.convex_hull = ConvexHull(self.coords)
        self.volume = self.convex_hull.volume
        self.faces = self.convex_hull.simplices # Array of arrays with indices of self.coords that make a triangle.
        self.oposite_faces = self.opposite_pairs() # [[[1 2 3] [4 5 6]] ... ] Array of arrays of arrays.
        self.planes = self.calc_planes()
        # Each array of oposite faces contains two arrays for the indices of the two oposite faces

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
        #Unimplemented
        return 123

    def calc_planes(self):

        planes = []
        for face in self.faces:
            # A face a tuple of indices that form a tringle in self.coords
            p1, p2, p3 = self.coords[face[0]], self.coords[face[1]], self.coords[face[2]]
            # Calculate two in-plane vectors of the plane
            v1 = p2 - p1
            v2 = p3 - p1
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)
            a, b, c = normal
            d = - np.dot(p1, normal)
            planes.append((a, b, c, d))

        return np.array(planes)

    def opposite_pairs(self):
        pairs = []
        # for each combination of faces:
        for i, j in combinations(range(len(self.faces)), 2):
            # If the set of the intersection is empty (len == 0)
            # They don't share any vertex in the octahedron.
            # Means the faces are opposite to each other.
            intersection = set(self.faces[i]) & set(self.faces[j])
            if len(intersection) == 0:
                pairs.append((i, j))
                pass
        return np.array(pairs)



import matplotlib
#matplotlib.use('Qt5Agg')  # or 'Qt5Agg' if Tk isn't available
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


'''def plot_planes(planes, vertices):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot vertices
    ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], color='red', s=50, zorder=5)

    # Define plot range from vertices
    x_range = np.linspace(vertices[:, 0].min() - 1, vertices[:, 0].max() + 1, 10)
    y_range = np.linspace(vertices[:, 1].min() - 1, vertices[:, 1].max() + 1, 10)
    xx, yy = np.meshgrid(x_range, y_range)

    colors = plt.cm.tab10(np.linspace(0, 1, len(planes)))

    for i, (a, b, c, d) in enumerate(planes):
        if abs(c) > 1e-10:  # solve for z: z = (-ax - by - d) / c
            zz = (-a * xx - b * yy - d) / c
            ax.plot_surface(xx, yy, zz, alpha=0.3, color=colors[i])
        elif abs(b) > 1e-10:  # solve for y
            y_range2 = np.linspace(vertices[:, 1].min() - 1, vertices[:, 1].max() + 1, 10)
            zz2 = np.linspace(vertices[:, 2].min() - 1, vertices[:, 2].max() + 1, 10)
            xx2, zz2 = np.meshgrid(x_range, zz2)
            yy2 = (-a * xx2 - c * zz2 - d) / b
            ax.plot_surface(xx2, yy2, zz2, alpha=0.3, color=colors[i])

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.tight_layout()
    #plt.show()
    plt.savefig(f'{os.path.join(olx.FilePath(), 'distortion.png')}')'''

## All of this Is made by Claude Ill have a look later

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
    print(calculation.planes)
    #plot_planes(calculation.planes, calculation.coords)