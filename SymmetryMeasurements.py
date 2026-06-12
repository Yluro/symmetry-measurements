
from olexFunctions import OlexFunctions
OV = OlexFunctions()

import os
import htmlTools
import olex
import olexex
import olx
import gui
import shutil
from constants import *


import time
debug = bool(OV.GetParam("olex2.debug", False))


instance_path = OV.DataDir()

try:
    from_outside = False
    p_path = os.path.dirname(os.path.abspath(__file__))
except:
    from_outside = True
    p_path = os.path.dirname(os.path.abspath("__file__"))

l = open(os.sep.join([p_path, 'def.txt'])).readlines()
d = {}
for line in l:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    d[line.split("=")[0].strip()] = line.split("=")[1].strip()

p_name = d['p_name']
p_htm = d['p_htm']
p_img = eval(d['p_img'])
p_scope = d['p_scope']

OV.SetVar('SymmetryMeasurements_plugin_path', p_path)

from PluginTools import PluginTools as PT


def get_selected_atoms() -> str:
    # Gets the selection from Olex2 -  Returns a string with atom labels.
    # If no atoms are selected, returns ''
    selection = olex.f('sel()')
    print(selection)
    return selection


def get_id_from_label(atom_label):
    orm_atoms = olexex.OlexRefinementModel().atoms()
    tag = next((atom['tag'] for atom in orm_atoms if atom['label'] == atom_label), None)
    return tag

def get_xyz_sel():
    selection = olex.f('sel()')
    sel_tag = get_id_from_label(selection)
    return get_xyz(sel_tag)


def get_xyz(atom_label):
    xyz = olx.xf.au.GetAtomCrd(atom_label)
    print(xyz)
    return xyz

def shape_exe_msg():
    shape_path = shutil.which("shape")
    if shape_path is None:
        print(f"Unable to find shape.exe in the system path.")
        return False
    else:
        print(f"SHAPE executable found at: {shape_path}")
        return True


def get_neighbours(atom_labels):
    # Gets the list of atoms from the loaded model.
    # The orm is a list of dictionaries, containing labels, atom_ids, parts, ADPs, etc.
    orm_atoms = olexex.OlexRefinementModel().atoms()

    ##selection = get_selected_atoms()
    if atom_labels == [""]:
        print("No atoms")
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
        #tags is an empty tuple if it wasn't found in the orm: selected a Qpick
        #tags is a list of len() = 0 if selected a
        if neighbour_tags is None or len(neighbour_tags) == 0:
            print(f'No connected atoms to {atom_label}')

        print(neighbour_tags) #(3, (1.332173751267887, 9.570147745635163, 1.1004595820674223), ((-1, 0, 0), (0, -1, 0), (0, 0, -1), (0.0, 1.0, 0.0)))
        neighbours_tags_list.append(neighbour_tags)

        for neighbour in neighbour_tags:
            if neighbour not in unique_neighbours:
                unique_neighbours.append(neighbour)


        # DEPRECATED - THIS CODE HERE RETURNED THE NEIGHBOURHOOD AS A LIST OF UNIQUE TAGS - DEPRECATED
        '''for tag in neighbour_tags:  
            if tag not in neighbour_tags:
                neighbour_tags.append(tag)
                # Use a similar next constructor to retrieve the
                # label from the orm and append it to the Neighbours list
                neighbours_label = next((atom['label'] for atom in orm_atoms if atom['tag'] == tag), None)
                neighbours_labels.append(neighbours_label)'''
    print(neighbours_tags_list)
    print(unique_neighbours)
    return neighbours_tags_list, unique_neighbours

def get_neighbours_on_sel():
    sel = olex.f('sel()')
    atom_labels = sel.split(' ')
    return get_neighbours(atom_labels)

def smart_build_polyhedra():
    selection = olex.f('sel()')
    atom_labels = selection.split(' ')
    if atom_labels == ['']:
        print('Unimplemented!')
        return None # Search orm for metal centres -> build_polyhedra from centre
    elif len(atom_labels) == 1 and atom_labels[0] in METALS:
        # If you only selected ONE METAL ATOM
        return None # build_poly_from_centre
    else:
        # If selection is more than One atom and has no metal atoms to call a centre just get all xyz coordinates and hope for the best.
        pass

    return None





class SymmetryMeasurements(PT):
    def __init__(self):
        super(SymmetryMeasurements, self).__init__()
        self.p_name = p_name
        self.p_path = p_path
        self.p_scope = p_scope
        self.p_htm = p_htm
        self.p_img = p_img
        self.deal_with_phil(operation='read')
        self.print_version_date()
        if not from_outside:
            self.setup_gui()
        OV.registerFunction(get_selected_atoms, True, "SymmetryMeasurements")
        OV.registerFunction(get_neighbours, True, "SymmetryMeasurements")
        OV.registerFunction(shape_exe_msg, True, "SymmetryMeasurements")
        OV.registerFunction(get_xyz_sel, True, "SymmetryMeasurements")
        OV.registerFunction(get_neighbours_on_sel, True, "SymmetryMeasurements")
    # END Generated =======================================

SymmetryMeasurements_instance = SymmetryMeasurements()
print("Loaded Symmetry Measurements by José Serrano-Guarinos.")
