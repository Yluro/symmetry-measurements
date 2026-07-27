from helper_functions import *


class AtomSelection:
    def __init__(self, selection_string):

        self.labels = selection_string.split(' ')
        self.clean_labels = [label.split('_$')[0] for label in self.labels]
        self.tags = [get_id_from_label(label) for label in self.labels]
        self.coords = [get_xyz(idx) for idx in self.tags]
        self.parts = [get_part(idx) for idx in self.tags]
        self.orm_atoms = olexex.OlexRefinementModel().atoms()
        self.polyhedron = 0

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

    def centroid_search(self):
        bonded_pairs = []
        for label, tag in zip(self.labels[1:], self.tags[1:]): # For each ligand
            print('Looking for neighbours for ' + label)
            neighbours = get_neighbours([label,])
            _, nei_uniques = neighbours

            for nei_tag in nei_uniques:
                if nei_tag in self.tags[1:]:
                    bonded_pairs.append((nei_tag, tag))
                else:
                    print(f'centroid_search: Could not find neighbours for {label}.')
        return bonded_pairs

