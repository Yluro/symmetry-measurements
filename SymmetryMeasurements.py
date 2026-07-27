import inspect

from olexFunctions import OlexFunctions

OV = OlexFunctions()

from helper_functions import *
import os
import htmlTools
import olex
import olexex
import olx
import gui
import shutil
from constants import *
import subprocess
from autoshape import *
from octahedral_distortion import *


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

def autoSHAPE():
    print('\n' + '-' * 50)
    print('Simple continuous Shape Analysis Using autoSHAPE')
    if not can_find_shape_msg():
        print('SHAPE executable not found in PATH.')
        return False
    selection = AtomSelection(olex.f('sel()'))

    # Exit if selection is empty
    if not selection.labels:
        print(f'Invalid atom selection: no atoms selected.')
        return False

    # Non-centered calculation if selection is more than one atom.
    if len(selection.labels) > 1:

        #Remove duplicate atoms


        shape_measurement = ShapeCalculation(selection.coords, selection.clean_labels, olx.FileName(), False, ['%fullout'])
        folder = shape_measurement.write_tab(olx.FilePath())
        files = run_shape(folder)
        for f in files:
            print_shape_table(os.path.join(folder, f'{f}.tab'))
            print('M. Llunell, D. Casanova, J. Cirera, P. Alemany, S. Alvarez. SHAPE, version 2.1; Universitat de Barcelona: Barcelona, Spain, 2013.')
        return folder
    elif len(selection.labels) == 1:
        selection.add_neighbours()
        shape_measurement = ShapeCalculation(selection.coords, selection.labels, olx.FileName(), True, ['%fullout'])
        folder = shape_measurement.write_tab(olx.FilePath())
        files = run_shape(folder)
        for f in files:
            print_shape_table(os.path.join(folder, f'{f}.tab'))
            print('M. Llunell, D. Casanova, J. Cirera, P. Alemany, S. Alvarez. SHAPE, version 2.1; Universitat de Barcelona: Barcelona, Spain, 2013.')
        return folder

    print('Invalid atom selection. Unknown error.')


    return False

def autoOCTADIST():

    # Get the selected atoms.
    selection = AtomSelection(olex.f('sel()'))  # Gets the selection

    # Exit if selection is empty
    if not selection.labels:
        print(f'Invalid atom selection: no atoms selected.')
        return False

    # Exit if selection is more than one atom.
    if len(selection.labels) != 1:
        print(f'Invalid atom selection: expected 1 atom, found {len(selection.labels)}.')
        return False

    #Add coordinated atoms to the current selection.
    selection.add_neighbours()

    # Exit if there are not 7 atoms.
    if len(selection.labels) != 7:
        print(f'Invalid polyhedra: expected 6 atoms connected to the central atom, found {len(selection.labels) - 1}.')
        return False

    #print('Valid 6-coordinate atom.')

    # Calculate the distortion parameters
    calculation = CalcDistortion(selection.coords, selection.labels)

    # Print results to console.
    calculation.print_results(os.path.basename(olx.FilePath()))
        #print(f'Opposite vertices {calculation.opposite_vertices}')
        #print([calculation.labels[v] for v in calculation.opposite_vertices.flatten()])
        #print(f'Opposite faces {calculation.opposite_faces}')
        #print(f'Found {len(calculation.faces)} faces.')

    # Make octahedron graph.
    calculation.draw_octahedron()

    #Citation
    print('\nThis calculations were made using a reimplementation of the OctaDist algorithm by David J. Harding et al.')
    print('Ketkaew, R., Tantirungrotechai, Y., Harding, P., Chastanet, G., Guionneau, P., Marchivie, M., & Harding, D. J. (2021). OctaDist: a tool for calculating distortion parameters in spin crossover and coordination complexes. Dalton Transactions, 50(3), 1086-1096.')
    return True

def shape_status_html():
    import shutil
    where = shutil.which('shape')
    found = where is not None
    color = OV.GetParam('gui.green') if found else OV.GetParam('gui.grey')
    text = f'SHAPE executable found at: {where}' if found else 'Unable to find shape.exe in the system path.'
    return f"<font color='{color}'>{text}</font>"

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
        OV.registerFunction(can_find_shape_msg, True, "SymmetryMeasurements")
        OV.registerFunction(get_xyz_sel, True, "SymmetryMeasurements")
        OV.registerFunction(get_neighbours_on_sel, True, "SymmetryMeasurements")
        OV.registerFunction(build_polyhedra_from_centre, True, "SymmetryMeasurements")
        #OV.registerFunction(build_dat_file, True, "SymmetryMeasurements")
        OV.registerFunction(write_dat, True, "SymmetryMeasurements")
        OV.registerFunction(autoSHAPE, True, "SymmetryMeasurements")
        OV.registerFunction(autoOCTADIST, True, "SymmetryMeasurements")
        OV.registerFunction(build_poly_on_sel, True, "SymmetryMeasurements")
        OV.registerFunction(shape_status_html, False, 'SymmetryMeasurements')
        OV.registerFunction(print_console_bs, False, 'SymmetryMeasurements')
        OV.registerFunction(print_orm, False, 'SymmetryMeasurements')
        OV.registerFunction(test_selection_class, False, 'SymmetryMeasurements')
    # END Generated =======================================



SymmetryMeasurements_instance = SymmetryMeasurements()
print("Loaded Symmetry Measurements by JSG.")