
# Constants for searching metal ions in
S_METALS = ['Li', 'Na', 'K', 'Rb', 'Cs', 'Fr', 'Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra']
P_METALS = ['Al', 'Ga', 'In', 'Tl', 'Ge', 'Sn', 'Pb', 'Sb', 'Bi', 'Po']
D3 = ["Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"]
D4 = ["Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd"]
D5 = ["Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg"]
LN = ["La", "Ce", "Nd", "Pr", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
AN = ["Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
METALS = S_METALS + P_METALS + D3 + D4 + D5 + LN

REF_SHAPE_DICT = {2: "1 2 3",
                  3: "1 2 3 4",
                  4: "1 2 3 4",
                  5: "1 2 3 4 5",
                  6: "1 2 3 4 5",
                  7: "1 2 3 4 5 6 7",
                  8: "1 2 3 4 5 6 7 8 9 10 11 12 13",
                  9: "1 2 3 4 5 6 7 8 9 10 11 12 13",
                  10: "1 2 3 4 5 6 7 8 9 10 11 12 13",
                  11: "1 2 3 4 5 6 7",
                  12: "1 2 3 4 5 6 7 8 9 10 11 12 13",
                  20: "1",
                  24: "1 2",
                  48: "1",
                  60: "1"
                } # This dict was created using the SHAPE 2.1 documentation

test_Mn1_polyhedra = (('Mn1', '0 8.0648 0'),
                      ('N2', '-1.332564 6.559586 -1.098927'),
                      ('N2', '1.3326 9.5700 1.0989'),
                      ('O4', '0.527332 6.436452 1.330861'),
                      ('O4', '-0.5273 9.6931 -1.3309'),
                      ('O5', '1.617025 7.420422 -1.381456'),
                      ('O5', '-1.6170 8.7092 1.3815')
                      )
