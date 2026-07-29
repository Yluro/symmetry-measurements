from helper_functions import *
from typing import List

class MolecularStructure: # The mere purpose of this class is to hold a strucutre to pass onto SHAPE and Octadist
    def __init__(self, coords, labels):
        self.coords = coords
        self.labels = labels


class AtomSelection:
    def __init__(self, selection_string):

        self.labels = selection_string.split(' ')
        self.clean_labels = [label.split('_$')[0] for label in self.labels]
        self.tags = [get_id_from_label(label) for label in self.labels]
        self.coords = [get_xyz(idx) for idx in self.tags]
        self.parts = [get_part(idx) for idx in self.tags]
        self.orm_atoms = olexex.OlexRefinementModel().atoms()

    def add_neighbours(self):
        if not self.labels:
            print("Could not find neighbours. Selection is empty.")

        for sel_label in self.labels.copy():
            neighbour_tags = next((atom['neighbours']
                                   for atom in self.orm_atoms
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
                    self.tags.append(nei_label[0])
                    self.coords.append(coord)
                    self.parts.append(part)

                    pass
                else:
                    nei_label = get_label_from_id(neighbour_tag)
                    coord = get_xyz(neighbour_tag)
                    part = get_part(neighbour_tag)

                    self.labels.append(nei_label)
                    self.tags.append(neighbour_tag)
                    self.coords.append(coord)
                    self.parts.append(part)

    def remove_duplicates(self):
        unique_labels = []
        unique_tags = []
        unique_coords = []
        unique_parts = []

        for label, tag, coord, part in zip(self.labels, self.tags, self.coords, self.parts):
            if label not in unique_labels:
                unique_labels.append(label)
                unique_tags.append(tag)
                unique_coords.append(coord)
                unique_parts.append(part)

        self.labels = unique_labels
        self.tags = unique_tags
        self.coords = unique_coords
        self.parts = unique_parts

    def merge_ligands(self):

        ####################
        # NEIGHBOUR SEARCH #
        ####################

        bonded_pairs = []
        #iterate over the ligands (atoms added with add_neighbours())
        for label, tag in zip(self.labels[1:], self.tags[1:]): # For each ligand

            # Get the neighbours of each ligand atom
            print('Looking for neighbours for ' + label)
            neighbours = get_neighbours([label,])
            _, nei_uniques = neighbours

            # If the neighbour of the ligand is also a ligand, add the bonded pair to the list.
            for nei_tag in nei_uniques:
                if nei_tag in self.tags[1:]:
                    bonded_pairs.append((nei_tag, tag))
                #else:
                #    print(f'{get_label_from_id(nei_tag)} is neighbour of {label} but is not bonded to the main polyhedra.')

        # If there are no bonded pairs of ligands, stop the function, return []
        if not bonded_pairs:
            print('Nothing to merge.')
            return []

        # Create an adjacency list from the bonded pairs. It will
        adj = {}
        for a, b in bonded_pairs: # Creates a dict with keys of all atoms and values are sets with all neighbours for all atoms.
            # adj = {atom1: {atom2, atom3}, atom2: {atom1}, atom3: {atom1}}
            adj.setdefault(a, set()).add(b) # If a isn't in the dictionary, add it with empty set. To this set, add b
            adj.setdefault(b, set()).add(a)


        #####################
        # FRAGMENT BUILDING #
        #####################

        visited = set() # Keeps track of atoms assigned to a fragment
        fragments = []  # Keeps list of final groups of fragments

        # Iterate over all atoms in the adjacency list:
        for atom in adj:
            if atom in visited: # Skip if the atom was visited already
                continue

            stack = [atom]      # Add the atom to the stack (to-process list)
            fragment = set()    # Create a new fragment as an emtpy set

            while stack: #While there are items in the stack
                current = stack.pop()       # Pop one atom
                if current in fragment:     # If the atom is already in the fragment, skip
                    continue
                fragment.add(current)       # Add the current atom to the fragment

                # Extend the stack to work on the adjacent atoms of the current one minus the ones already the fragment
                stack.extend(adj[current] - fragment)

            visited |= fragment             # Mark all atoms as visited (|= merges sets)
            fragments.append(fragment)      # Adds the fragment to the final fragments list


        ##################
        # LIGAND MERGING #
        ##################

        tag_to_idx = {tag: i for i, tag in enumerate(self.tags)}
        insert_at = {}  # index -> (label, coords) to place there
        skip = set()  # indices to drop

        for i, frag in enumerate(fragments):
            idxs = sorted(tag_to_idx[tag] for tag in frag)

            cx = sum(self.coords[j][0] for j in idxs) / len(frag)
            cy = sum(self.coords[j][1] for j in idxs) / len(frag)
            cz = sum(self.coords[j][2] for j in idxs) / len(frag)

            first = idxs[0]
            insert_at[first] = (f'Z{i}', (cx, cy, cz))
            skip.update(idxs[1:])  # keep 'first', drop the rest

        new_coords = []
        new_labels = []
        new_tags = []

        for j in range(len(self.tags)):
            if j in skip:
                continue
            if j in insert_at:
                label, centroid = insert_at[j]
                new_labels.append(label)
                new_coords.append(centroid)
                new_tags.append(-(j + 1))  # placeholder tag, adjust as needed
            else:
                new_labels.append(self.labels[j])
                new_coords.append(self.coords[j])
                new_tags.append(self.tags[j])

        self.coords = new_coords
        self.labels = new_labels
        self.tags = new_tags

        return fragments


def split_by_parts(selection: AtomSelection) -> List[MolecularStructure]:
    if len(set(selection.parts)) > 2: # If there are more than 2 parts in the selection (i.e. part 0, part 1 and part 2)
        # Separate atoms by parts:
        parted_labels = []
        parted_coords = []
        for part in set(selection.parts):
            labels = []
            coords = []
            for i in range(len(selection.labels)):
                if selection.parts[i] == part:
                    labels.append(selection.labels[i])
                    coords.append(selection.coords[i])
            parted_labels.append(labels)
            parted_coords.append(coords)


        structures = []
        for i in range(1, len(parted_labels)):
            part_0n_labels = parted_labels[0] + parted_labels[i]
            part_0n_coords = parted_coords[0] + parted_coords[i]
            struc = MolecularStructure(part_0n_coords, part_0n_labels)
            structures.append(struc)
        return structures
    else:
        return [MolecularStructure(selection.coords, selection.labels)]