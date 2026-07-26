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
        if i > 9: # Safe ward in case this While loop gets out of control.
            break

    #print(f'Good file directory: {file_dir}')


    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(file_path, 'w') as f:
        f.write(dat_file_contents)
        print(f'Writing {file_name} at {file_path}...')

    #print(file_path)

    return file_dir


