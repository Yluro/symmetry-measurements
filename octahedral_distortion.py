import numpy as np
from scipy.spatial import ConvexHull
from itertools import combinations, permutations
import matplotlib.pyplot as plt

import os
from collections.abc import Iterable


class CalcDistortion:
    def __init__(self, polyhedron):
        self._DEFAULT_OH_LABELS = ['Z'] + [f'L{i}' for i in range(1, 7)]

        self.labels = self._DEFAULT_OH_LABELS
        self.coords = []
        self._parse_input(polyhedron) # Parse Input updates values of coords and labels

        #self.coords = np.array(points) # xyz Coordinates of central (first) and ligands (rest)
        self.central_atom = self.coords[0]
        self.vertices = self.coords[1:]

        self.vectors = np.array(coord - self.central_atom for coord in self.vertices) # Vectors pointing from metal to ligand
        self.norm_vectors = np.array([v / np.linalg.norm(v) for v in self.vectors])

        self.bond_distances = self.calc_bond_distances()
        self.mean_bond_distance = np.mean(self.bond_distances)

        self.angles = self._all_angles() # Angles is a sorted list. The last three elements will be
        self.cis_angles = self.angles[:-3]
        self.trans_angles = self.angles[-3:]

        self.convex_hull = ConvexHull(self.vertices)
        self.volume = self.convex_hull.volume

        # Array of arrays with indices of self.vertices that make a triangle.
        self.faces = self.convex_hull.simplices
        self.normals = self.calc_normals()
        # Array[(a,b,c,d)] that solve for plane ax + by + cz + d = 0 for each face
        self.planes = self.calc_planes()

        # Each array of opposite faces contains two arrays for the indices of the two opposite faces
        # [[[1 2 3] [4 5 6]] ... ] Array of arrays of arrays.
        self.opposite_faces = self._opposite_faces()
        self.opposite_vertices = self._opposite_vertices()


        # Final calculations
        self.zeta = self.calc_zeta()
        self.delta = self.calc_delta()
        self.sigma = self.calc_sigma()
        self.theta = self.calc_theta()

    def _parse_input(self, polyhedra):
        print(type(polyhedra), polyhedra)
        """
        The standard polyhedron from build_polyhedra_from_centre() gives an array:
        [('centre', 'x y z'), ('L1', 'x y z'),...]

        The function will also get
        :param input:
        :return:
        """
        def parse_coordinate(xyz):
            crd = None
            if isinstance(xyz, str):
                crd = tuple(map(float, xyz.split(' ')))
            elif isinstance(xyz, Iterable):
                crd = tuple([float(v) for v in xyz])
            else:
                raise TypeError(f'Could not parse coordinate: {xyz}')

            if crd is None:
                raise TypeError(f'Could not parse coordinate: {xyz}')

            if len(crd) != 3:
                raise ValueError(f'Invalid coordinate. Expected 3 coordinates, found {len(crd)}.')

            return crd

        labels = []
        coords = []

        for p in polyhedra:
            if isinstance(p, str):
                coords.append(parse_coordinate(p))

            elif isinstance(p, Iterable):
                vals = tuple(p)

                if len(vals) == 2 and isinstance(vals[0], str):
                    labels.append(vals[0])
                    coords.append(parse_coordinate(vals[1]))
                else:
                    coords.append(parse_coordinate(vals))

            else:
                raise TypeError(f"Cannot parse {p!r}")

        if len(labels) == 7:
            self.labels = np.array(labels, dtype=str)
        elif not labels:
            print(f'Warning, expected 7 labels, found {len(labels)}. Using default label Names.')

        if len(coords) != 7:
            raise ValueError(f'Invalid number of points. Expected 7 points, found {len(polyhedra)}.')

        self.coords = np.array(coords, dtype=np.float64)


    def calc_bond_distances(self):
        ds = []
        for v in self.vectors:
            d = np.linalg.norm(v)
            ds.append(d)
        return np.array(ds, dtype=np.float64)

    def _all_angles(self):
        angles = []
        for i, j in combinations(range(len(self.vectors)), 2):
            v1 = self.vectors[i] / np.linalg.norm(self.vectors[i])
            v2 = self.vectors[j] / np.linalg.norm(self.vectors[j])
            angle = np.degrees(np.arccos(np.clip(np.dot(v1, v2), -1, 1)))
            angles.append(angle)

        angles.sort()
        return np.array(angles)

    def calc_zeta(self) -> float:
        deviations = [np.abs(d - self.mean_bond_distance) for d in self.bond_distances]
        return np.sum(deviations)

    def calc_delta(self) -> float:
        return np.sum(np.power((bond_distance - self.mean_bond_distance)/self.mean_bond_distance, 2) for bond_distance in self.bond_distances) / 6

    def calc_sigma(self) -> float:
        sigma = np.sum(np.abs(90 - self.cis_angles))
        return sigma

    def calc_theta(self) -> float:
        thetas = []

        for face_pair in self.opposite_faces:
            angles = []
            # assign front and back faces
            front, back = face_pair
            # the normal is calculated from the front face
            normal = self.normals[front]
            print(f'Front face: {self.faces[front]}')
            print(f'Back face {self.faces[back]}')

            # For each index of the front face
            for i in self.faces[front]:
                # Get the vector i and its projection to the front face normal
                v_i = self.vectors[i]
                p_i = self._project_onto_plane(v_i, normal)
                p_i = p_i / np.linalg.norm(p_i)
                #print(f'Projection of {i} to plane {front}: {p_i}')

                for j in self.faces[back]:
                    pair = [i, j]
                    pair_r = [j, i]
                    is_opposite = any(np.array_equal(pair, ov) or np.array_equal(pair_r, ov)
                                      for ov in self.opposite_vertices)
                    if is_opposite:
                        #print(f'Skipped {j} because is op of {i}')
                        continue
                    v_j = self.vectors[j]
                    p_j = self._project_onto_plane(v_j, normal)
                    p_j = p_j / np.linalg.norm(p_j)
                    angle = np.degrees(np.arccos(np.clip(np.dot(p_i, p_j), -1, 1)))
                    print(f'Angle between {i} and {j} is {angle} degs')
                    abs_angle = np.abs(angle)
                    angles.append(abs_angle)

            print(f'Measured {len(angles)} for face {front}')
            theta = np.sum([np.abs(60 - angle) for angle in angles])
            thetas.append(theta)
            print(theta)

        final_theta = np.average(thetas) * 4
        return final_theta

    def calc_normals(self):
        normals = []
        for face in self.faces:
            # A face a tuple of indices that form a tringle in self.coords
            p1, p2, p3 = self.vertices[face[0]], self.vertices[face[1]], self.vertices[face[2]]
            # Calculate two in-plane vectors of the plane
            v1 = p2 - p1
            v2 = p3 - p1
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)
            normals.append(normal)
        return np.array(normals)

    def calc_planes(self):
        planes = []
        for face, normal in zip(self.faces, self.normals):
            p1 = self.vertices[face[0]]
            a, b, c = normal
            d = - np.dot(p1, normal)
            planes.append((a, b, c, d))

        return np.array(planes)

    def _opposite_faces(self):
        pairs = []
        # for each combination of faces:
        for i, j in permutations(range(len(self.faces)), 2):
            # If the set of the intersection is empty (len == 0)
            # They don't share any vertex in the octahedron.
            # Means the faces are opposite to each other.
            intersection = set(self.faces[i]) & set(self.faces[j])
            if len(intersection) == 0:
                pairs.append((i, j))
                pass
        return np.array(pairs)

    def _opposite_vertices(self):
        pairs = []
        # For every combination of vertex i and j
        for i, j in combinations(range(len(self.vertices)), 2):
            # Get all faces that contain vertex i
            faces_with_i = [face for face in self.faces if i in face]

            # For each of those faces, get all vertices that form them
            vertices_near_i = set(v for face in faces_with_i for v in face)

            # If j is not in the set, then i and j share no common faces
            # Thus, i and j are not opposite.
            if j not in vertices_near_i:
                pairs.append((i, j))

        return np.array(pairs)

    def _angle_sign(self, v1, v2, ref):
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 < 1e-10 or n2 < 1e-10:
            return 0.0
        angle = np.degrees(np.arccos(np.clip(np.dot(v1, v2) / (n1 * n2), -1, 1)))
        if np.dot(np.cross(v1, v2), ref) < 0:
            angle = -angle
        return angle

    def _project_onto_plane(self, vector, normal):
        return vector - np.dot(vector, normal) * normal

    def print_results(self, file=__file__):
        print('\n' + '=' * 70)
        print(f'Octahedral distortion parameters calculated for {self.labels[0]} in {os.path.basename(file)}')
        print('-' * 70)
        print(f"{'Mean d(M-X)':<12}{self.mean_bond_distance:>12.4f}{'   '}{'Ang':<12}")
        print(f"{'Zeta':<12}{self.zeta:>12.4f}{'   '}{'Ang':<12}")
        print(f"{'Zeta':<12}{self.delta:>12.4f}{'   '}{'':<12}")
        print(f"{'Sigma':<12}{self.sigma:>12.4f}{'   '}{'deg':<12}")
        print(f"{'Theta':<12}{self.theta:>12.4f}{'   '}{'deg':<12}")
        print(f"{'Volume':<12}{self.volume:>12.4f}{'   '}{'Ang^3':<12}")
        print('=' * 70)


    def draw_octahedron(self):
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_box_aspect((1, 1, 1))
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.tight_layout()

        ax.scatter(self.central_atom[0], self.central_atom[1], self.central_atom[2], color='blue', s=50, zorder=5)
        ax.scatter(self.vertices[:,0], self.vertices[:,1], self.vertices[:,2], color='red', s=50, zorder=5)

        colors = plt.cm.tab10(np.linspace(0, 1, len(self.faces)))

        for i, face in enumerate(self.faces):
            triangle = [self.vertices[face[0]], self.vertices[face[1]], self.vertices[face[2]]]
            poly = Poly3DCollection([triangle], alpha=0.3, facecolor=colors[i], edgecolor='black')
            ax.add_collection3d(poly)

        for label, coord in zip(self.labels, self.coords):
            ax.text(coord[0], coord[1], coord[2], label, ha='right', va='top', zorder=10)

        # Olex2 uses non GUI version of matplotlib so
        # I can only save graphs and show them later
        # - I cannot get 3d view.
        plt.show()
        ## For using inside Olex
        # save_dir = os.path.join(olx.FilePath(), 'Oh_distortion')
        # if not os.path.exists(save_dir):
        #    os.makedirs(save_dir)
        # plt.savefig(os.path.join(save_dir, 'octahedron.png'))
        # print(f'Octahedron graph saved to {save_dir}.')
        # plt.savefig('octahedron.png')

# Draw planes function, absolute mess made by claude I don't understand anything.
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
    save_dir = os.path.join(olx.FilePath(), 'Oh_distortion')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.savefig(os.path.join(save_dir, 'planes.png'))
    print(f'Saved to {save_dir}')'''



    #print('Opposite faces:')
    #print(calculation.opposite_faces)
    #print('All faces')
    #print(calculation.faces)
    #print('Opposite vertices')
    #print(calculation.opposite_vertices)
    #print(calculation.normals)
    #draw_octahedron(calculation.central_atom, calculation.vertices, calculation.faces)