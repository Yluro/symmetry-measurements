
from olexFunctions import OlexFunctions
OV = OlexFunctions()

import os
import htmlTools
import olex
import olx
import gui

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
      OV.registerFunction(self.get_selected_atoms,True,"SymmetryMeasurements")
    # END Generated =======================================

    def get_selected_atoms(self) -> str:
      selection = olex.f('sel()')
      if selection is not '':
        print(olex.f('sel()'))
        return selection
      else:
        print('No atoms selected')
        return selection

    def get_neighbours(self, atom_labels):
        if not atom_labels.strip():
          return []
        pass


SymmetryMeasurements_instance = SymmetryMeasurements()
print("Loaded Symmetry Measurements by José Serrano-Guarinos.")
