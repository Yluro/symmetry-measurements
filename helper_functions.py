import os
import htmlTools
import olex
import olexex
import olx
from collections.abc import Iterable
import gui
import shutil
from constants import *
import subprocess



## SMALL HELPER FUNCTIONS
def get_selected_atoms() -> str:
    # Gets the selection from Olex2 -  Returns a string with atom labels.
    # If no atoms are selected, returns ''
    selection = olex.f('sel()')
    print(selection)
    return selection


def get_id_from_label(atom_label) -> int:
    orm_atoms = olexex.OlexRefinementModel().atoms()
    tag = next((atom['tag'] for atom in orm_atoms if atom['label'] == atom_label), None)
    return tag


def get_label_from_id(atom_label):
    orm_atoms = olexex.OlexRefinementModel().atoms()
    label = next((atom['label'] for atom in orm_atoms if atom['tag'] == atom_label), None)
    return label


def get_xyz_sel():
    selection = olex.f('sel()')
    if selection == '':
        print('No atoms selected.')
        return None
    try:
        sel_tag = get_id_from_label(selection)
        print(selection)
        return get_xyz(sel_tag)
    except RuntimeError:
        print(f'Could not find {selection} in the orm')
        return None


def get_xyz(atom_tag):
    crd = olx.xf.au.GetAtomCrd(atom_tag)
    xyz_string = olx.xf.au.Orthogonalise(crd).split(' ')
    xyz = tuple(float(x) for x in xyz_string)
    return xyz

def get_part(atom_label):
    return olx.xf.au.GetAtomPart(atom_label)


def get_neighbours(atom_labels):
    # Gets the list of atoms from the loaded model.
    # The orm is a list of dictionaries, containing labels, atom_ids, parts, ADPs, etc.
    orm_atoms = olexex.OlexRefinementModel().atoms()

    ##selection = get_selected_atoms()
    if atom_labels == [""]:
        print("Could not find neighbours. No atoms selected.")
        return None

    ##selection = selection.split(' ')
    ##print(selection)

    neighbours_tags_list = []
    unique_neighbours = []
    ##neighbours_labels = []
    for atom_label in atom_labels:
        # next finds the first occurrence in orm_atoms in which the label matches
        # with the sel and returns the atoms neighbours as a tuple of tags:
        neighbour_tags = next((atom['neighbours'] for atom in orm_atoms if atom['label'] == atom_label), ())
        #tags is an empty tuple if it wasn't found in the orm: selected a Q-peak
        #tags is a list of len() = 0 if selected a
        if neighbour_tags is None or len(neighbour_tags) == 0:
            print(f'No connected atoms to {atom_label}.')

        #print(neighbour_tags) #(3, (1.332173751267887, 9.570147745635163, 1.1004595820674223), ((-1, 0, 0), (0, -1, 0), (0, 0, -1), (0.0, 1.0, 0.0)))
        neighbours_tags_list.append(neighbour_tags)

        for neighbour in neighbour_tags:
            if neighbour not in unique_neighbours:
                unique_neighbours.append(neighbour)


        # DEPRECATED - THIS CODE HERE RETURNED THE NEIGHBOURHOOD AS A LIST OF UNIQUE TAGS - DEPRECATED
        # NOW THIS FUNCTIONS RETURNS A LIST OF UNIQUE NEIGHBOUR LABELS
        '''for tag in neighbour_tags:  
            if tag not in neighbour_tags:
                neighbour_tags.append(tag)
                # Use a similar next constructor to retrieve the
                # label from the orm and append it to the Neighbours list
                neighbours_label = next((atom['label'] for atom in orm_atoms if atom['tag'] == tag), None)
                neighbours_labels.append(neighbours_label)'''
    #print(f'Neighbours for each atom selected:{neighbours_tags_list}')
    #print(f'Unique neighbours:{unique_neighbours}')
    return neighbours_tags_list, unique_neighbours


def get_neighbours_on_sel():
    sel = olex.f('sel()')
    atom_labels = sel.split(' ')
    return get_neighbours(atom_labels)


def build_polyhedra_from_centre(atom_label=('Mn1',)):
    neighbours = get_neighbours(atom_label)
    if neighbours is None:
        print(f'No neighbours can be found for {atom_label}.')
        return None

    _, unique_neighbours = neighbours
    #print(unique_neighbours)
    if len(atom_label) > 1:
        print(f'Invalid selection: expected 1 atom, found {len(atom_label)}.')
        return None

    centre = atom_label[0]
    centre_id = get_id_from_label(centre)
    crd = olx.xf.au.GetAtomCrd(centre_id)
    xyz = olx.xf.au.Orthogonalise(crd)

    polyhedra = [(centre, xyz)]


    for neighbour in unique_neighbours:
        if type(neighbour) == tuple:
            #print(f'Found tuple: {neighbour}')
            # get_neigours() returns a complicated tuple if the neighbour is outside the ASU.
            # This list already contains the "extended coordinates of the neighbour atoms"
            xyz = ' '.join(f'{x:.4f}' for x in neighbour[1]) # Join the xyz tuple values into a string
            label = get_label_from_id(neighbour[0])
            polyhedra.append((label, xyz))
        else:
            xyz = get_xyz(neighbour)
            label = get_label_from_id(neighbour)
            polyhedra.append((label, xyz))

    #print(polyhedra)
    return polyhedra


def build_poly_on_sel():
    sel = olex.f('sel()')
    label = sel.split(' ')
    poly = build_polyhedra_from_centre(label)
    print(poly)
    return poly


def parse_coordinate(xyz):
    """
    Parses a coordinate into a tuple of floats,
    Accepts any Iter(float) or strings separated by spaces.
    :param xyz: Iter(Any) or str
    :return crd: tuple(x, y, z)
    """
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


def print_console_bs():
    import inspect
    print(inspect.getsource(olexex.install_plugin))


class AtomSelection:
    def __init__(self, selection_string):

        self.labels = selection_string.split(' ')
        self.tags = [get_id_from_label(label) for label in self.labels]
        self.coords = [get_xyz(idx) for idx in self.tags]
        self.parts = [get_part(idx) for idx in self.tags]

        self.polyhedron = 0


    def add_neighbours(self):
        if not self.labels:
            print("Could not find neighbours. Selection is empty.")
            return []

        orm_atoms = olexex.OlexRefinementModel().atoms()

        for sel_label in self.labels.copy():
            neighbour_tags = next((atom['neighbours']
                                   for atom in orm_atoms
                                   if atom['label'] == sel_label),
                                  None)

            if neighbour_tags is None:
                print(f'Could not find neighbours for {sel_label}.')

            unique_neighbours = []
            for neighbour_tag in neighbour_tags:
                if neighbour_tag not in unique_neighbours:
                    unique_neighbours.append(neighbour_tag)

            for neighbour_tag in unique_neighbours:
                if type(neighbour_tag) == tuple:
                    nei_label = get_label_from_id(neighbour_tag[0])
                    coord = neighbour_tag[1]
                    part = get_part(neighbour_tag[0])

                    self.labels.append(nei_label)
                    self.coords.append(coord)
                    self.parts.append(part)

                    pass
                else:
                    nei_label = get_label_from_id(neighbour_tag)
                    coord = get_xyz(neighbour_tag)
                    part = get_part(neighbour_tag)

                    self.labels.append(nei_label)
                    self.coords.append(coord)
                    self.parts.append(part)


        return None


def test_selection_class():
    selection = AtomSelection(olex.f('sel()'))
    print(selection.labels)
    print(selection.coords)
    print(selection.parts)

    selection.add_neighbours()
    print(selection.labels)
    print(selection.coords)
    print(selection.parts)