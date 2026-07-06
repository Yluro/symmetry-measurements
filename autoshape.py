import shutil
import olx
import os
import subprocess
from constants import *
from helper_functions import *
import numpy as np
from collections.abc import Iterable


class DatHandler:
    def __init__(self, polyhedron, centered=True, keywords='\n%fullout'):
        self.labels = []
        self.coords = []
        self._parse_input(polyhedron)  # Parse Input updates values of coords and labels
        self.dat_title = 0

        self.dat_keywords = keywords
        if centered:
            self.centre = 1
            self.ligands = len(self.coords) - 1
        else:
            self.centre = 0
            self.ligands = len(self.coords)



    def _parse_input(self, polyhedra):
        """
        The standard polyhedron from build_polyhedra_from_centre() gives an array:
        [('centre', 'x y z'), ('L1', 'x y z'),...]

        The function will also get
        :param input:
        :return:
        """
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
        pass


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


def parse_shape_tab(tab_path):

    #print(f"Parsing: {tab_path}")
    #print(f"Exists: {os.path.exists(tab_path)}")

    with open(tab_path, 'r') as f:
        lines = f.readlines()

        # Find the polyhedra table
        # (Label    N   Symm    Name)
        shape_labels = []
        shape_names = []
        for tab_line in lines[5:]: # The array splicing skips the header of the tab file. That messes up the search
            if len(tab_line.split()) >= 4 and tab_line.split()[1].isdigit():
                shape_labels.append(tab_line.split()[0])
                name = ' '.join(tab_line.split()[3:])
                shape_names.append(name)

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

        return atom_label, shape_names, shape_labels, values


def print_shape_table(tab_path):
    result = parse_shape_tab(tab_path)
    if result is None:
        return False
    atom_label, shape_names, shape_labels, values = result
Re    max_name_length = max(len(name) for name in shape_names) + 2
    min_val = min(values)
    print('\n'+'=' * 65)
    print(f'SHAPE 2.1 results for {atom_label} in {os.path.basename(tab_path)}:')
    print('-'*65)
    print(f"{'Polyhedron':<{max_name_length}}{'Symbol':<10}{'CShM':>10}")
    print('-'*65)
    for name, label, val in zip(shape_names, shape_labels, values):
        marker = ' <---- best fit' if val == min_val else ''
        print(f'{name:<{max_name_length}}{label:<10}{val:>10}{marker:>10}')
    print('='*65)
    return None