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


def can_find_shape_msg(silent=True):
    shape_path = shutil.which("shape")
    if shape_path is None:
        print(f"Unable to find shape.exe in the system path.")
        return False
    else:
        if not silent:
            print(f"SHAPE executable found at: {shape_path}")
        return True


def build_dat_file(polyhedra= test_Mn1_polyhedra):
    """
    Builds a dat file for the given polyhedra.
    :param polyhedra:
    :return dat_file: str | None if incorrect number of vertices:
    """
    title = f'$ {olx.FileName()}_{polyhedra[0][0]}\n'
    fullout ='%fullout\n'
    ligands = len(polyhedra) - 1 # The dat file for SHAPE2.1 needs the amount of ligands there are
    metal = 1 # Means the position of the metal. The build_polyhedra() functions will always put the metals at first
    positions = f'{ligands} {metal}\n'
    try:
        geometries = f'{REF_SHAPE_DICT[ligands]}\n' # The SHAPE2.1 documentation gives these strings of numbers
        subtitle = f'{polyhedra[0][0]}\n'.upper()
        table = '\n'.join(f'{label} {xyz}' for label, xyz in polyhedra)  # Joins all rows of the table
        dat_file_contents = title + fullout + positions + geometries + subtitle + table
        #print(dat_file_contents)
        return dat_file_contents, f'{olx.FileName()}_{polyhedra[0][0]}'

    except KeyError:
        print(f'No defined geometries for {ligands} vertices. Check the structure for extra bonds.')
        return None, None


def write_dat(dat_file_contents= None, title= None):
    """
    Writes a dat file given its contents. Will create autoSHAPE folder in FilePath().
    Will create subfolders if ran multiple times.
    :param dat_file_contents: Text of the .dat file
    :param title: Name of the .dat file.
    :return file_dir:
    """
    if (dat_file_contents, title) == (None, None):
        dat_file_contents, title = build_dat_file(test_Mn1_polyhedra)

    base_dir = olx.FilePath()
    i = 0
    file_name = f'{title.strip()}_{i}.dat'
    file_dir = os.sep.join((base_dir, 'autoSHAPE', title.strip(), str(i)))
    file_path = os.sep.join((file_dir, file_name))
    while os.path.exists(file_path):
        file_name = f'{title.strip()}_{i}.dat'
        file_dir = os.sep.join((base_dir, 'autoSHAPE', title.strip(), str(i)))
        file_path = os.sep.join((file_dir, file_name))
        i += 1
        if i > 10: # Safe ward in case this While loop gets out of control.
            break

    #print(f'Good file directory: {file_dir}')


    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(file_path, 'w') as f:
        f.write(dat_file_contents)
        print(f'Writing {file_name} at {file_path}...')

    #print(file_path)

    return file_dir


def run_shape(folder):
    """
    Runs a SHAPE instance on all dat files in a specified folder.
    :param folder:
    :return files: Name of the output files without file extension.
    """
    dat_files = [f for f in os.listdir(folder) if f.endswith('.dat')]
    for file in dat_files:
        print(f"Running SHAPE on {file}...")
        process = subprocess.Popen('shape', shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, cwd=folder)
        out, err = process.communicate(input=f'{file}\n')
        print(out)  # Send Enter key (newline character)

    output_files = [f[:-4] for f in dat_files]
    return output_files


def autoSHAPE():
    if can_find_shape_msg():
        sel = olex.f('sel()') # Gets the selection
        if sel != '':
            label = sel.split(' ')
            poly = build_polyhedra_from_centre(label)
            if poly is None:
                return None
            file_contents, title = build_dat_file(poly)
            folder = write_dat(file_contents, title)
            files = run_shape(folder)
            for f in files:
                print_shape_table(os.path.join(folder, f'{f}.tab'))
            return folder
        else:
            print('No atom selected!')
    else:
        print('SHAPE executable not found in PATH.')
    return None


def parse_shape_tab(tab_path):

    #print(f"Parsing: {tab_path}")
    #print(f"Exists: {os.path.exists(tab_path)}")

    with open(tab_path, 'r') as f:
        lines = f.readlines()

        # Find the polyhedra table
        # (Label    N   Symm    Name)
        shape_labels = []
        for tab_line in lines[5:]: # The array splicing skips the header of the tab file. That messes up the search
            if len(tab_line.split()) >= 4 and tab_line.split()[1].isdigit():
                shape_labels.append(tab_line.split()[0])

        #print(shape_labels)
        # Second pass through the tab file to find the data with the CShMs
        data_row = None
        for tab_line in lines[5:]:
            if ',' in tab_line and any(c.isdigit() for c in tab_line):
                #print(tab_line)
                data_row = tab_line

        if data_row is None:
            print(f"Could not parse data row in {tab_path}")
            return None

        parts = [c.strip() for c in data_row.split(',')]
        atom_label = parts[0]
        values = [float(v) for v in parts[1:]]

        return atom_label, shape_labels, values


def print_shape_table(tab_path):
    result = parse_shape_tab(tab_path)
    if result is None:
        return False
    atom_label, shape_labels, values = result
    min_val = min(values)
    print('\n'+'=' * 50)
    print(f'SHAPE2.1 results for {atom_label} in {os.path.basename(tab_path)}:')
    print('-'*50)
    print(f"{'Polyhedron':<12}{'CShM':>10}")
    print('-'*50)
    for label, val in zip(shape_labels, values):
        marker = ' <---- best fit' if val == min_val else ''
        print(f'{label:<12}{val:>10}{marker:>10}')
    print('='*50)
    return None


def autoOCTADIST():
    sel = olex.f('sel()')  # Gets the selection
    if sel != '':
        label = sel.split(' ')
        poly = build_polyhedra_from_centre(label)
        if len(poly) != 7:
            print('Invalid polyhedra: central atom has more than six connected atoms.')
            return False

        #print('Valid 6-coordinate atom.')

        coords = [poly[i][1] for i in range(len(poly))]
        calculation = CalcDistortion(coords)
        calculation.print_results(os.path.basename(olx.FilePath()))


        return True
    else:
        print('No atom selected.')
        return False


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
        OV.registerFunction(build_dat_file, True, "SymmetryMeasurements")
        OV.registerFunction(write_dat, True, "SymmetryMeasurements")
        OV.registerFunction(autoSHAPE, True, "SymmetryMeasurements")
        OV.registerFunction(autoOCTADIST, True, "SymmetryMeasurements")
        OV.registerFunction(build_poly_on_sel, True, "SymmetryMeasurements")
    # END Generated =======================================



SymmetryMeasurements_instance = SymmetryMeasurements()
print("Loaded Symmetry Measurements by JSG.")