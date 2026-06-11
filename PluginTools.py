import olex
import olx
import os
import OlexVFS
import time
import glob
import shutil
import gui
import HttpTools

from olexFunctions import OV
debug = OV.IsDebugging()

class VFSDependent(object):
  def __init__(self):
    olx.VFSDependent.add(self)

  def load_ressources(self):
    pass

class PluginTools(VFSDependent):
  def __init__(self):
    super(PluginTools, self).__init__()
    self.headless = False
    if olx.HasGUI() == 'true':
      from gui.tools import deal_with_gui_phil
      deal_with_gui_phil('load')
      olx.InstalledPlugins.add(self)

  def endKickstarter(self, make_gui=True):
    p = os.path.join(self.p_path, self.p_htm + ".htm")
    if OV.HasGUI() and make_gui:
      try:
        #gui.help.gh.git_help(quick=True, specific=self.p_path)
        t = gui.file_open(p, 'r')
        OlexVFS.write_to_olex(p, t)
        OV.UpdateHtml()
      except:
        print("No GUI available")

  def get_plugin_date(self):
    return time.ctime(os.path.getmtime(self.p_path))

  def print_version_date(self):
    print("Loading %s (Version %s)\n" % (self.p_name, self.get_plugin_date()), end=' ')

  def deal_with_phil(self, operation='read', which='user_local'):
    # define paths
    user_phil_file = os.path.join(OV.DataDir(), "%s.phil" % self.p_scope)
    phil_file_p = os.path.join(self.p_path, "%s.phil" % self.p_scope)
    gui_phil_file_p = os.path.join(self.p_path, "%s.phil" % self.p_name.lower())
    ###
    if operation == "read":
      phil_file = open(phil_file_p, 'r', encoding="utf-8")
      phil = phil_file.read()
      phil_file.close()

      olx.phil_handler.adopt_phil(phil_string=phil)
      olx.phil_handler.rebuild_index()

      if os.path.exists(gui_phil_file_p):
        gui_phil = open(gui_phil_file_p, 'r', encoding="utf-8").read()

        olx.gui_phil_handler.adopt_phil(phil_string=gui_phil)
        olx.gui_phil_handler.merge_phil(phil_string=gui_phil)
        olx.gui_phil_handler.rebuild_index()
        self.g = getattr(olx.gui_phil_handler.get_python_object(), 'gui')

      if os.path.exists(user_phil_file):
        olx.phil_handler.update(phil_file=user_phil_file)

      self.params = getattr(olx.phil_handler.get_python_object(), self.p_scope)

    elif operation == "save":
      olx.phil_handler.save_param_file(
        file_name=user_phil_file, scope_name='%s' % self.p_scope, diff_only=False)
      # olx.phil_handler.save_param_file(
        # file_name=user_phil_file, scope_name='snum.%s' %self.p_name, diff_only=True)

  def setup_gui(self, force=False):
    if not hasattr(self, 'p_onclick'):
        self.p_onclick = ""
    if olx.HasGUI() != 'true' or self.headless:
      return
    import gui.help
    from gui.tools import make_single_gui_image
    from gui.tools import add_tool_to_index
    for image, img_type in self.p_img:
      make_single_gui_image(image, img_type=img_type, force=force)
    olx.FlushFS()

    if self.p_htm:
      image = self.p_img[0][0]
      try:
        location = self.p_location
        before = self.p_before
      except:
        location = OV.GetParam("%s.gui.location" % (self.p_scope))
        before = OV.GetParam("%s.gui.before" % (self.p_scope))
      try:
        add_tool_to_index(scope=self.p_name, link=self.p_htm,
                          path=self.p_path, location=location,
                          before=before, filetype='', image=image, onclick=self.p_onclick)
      except:
        pass
    #gui.help.gh.git_help(quick=True, specific=self.p_path)

  def edit_customisation_folder(self, custom_name=None):
    self.get_customisation_path(custom_name=None)
    p = self.customisation_path
    if not p:
      p = self.p_path + "_custom"
      IGNORE_PATTERNS = ('*.pyc', '*.py', '*.git')
      shutil.copytree(self.p_path, p, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))
      os.rename("%s/templates/default" % p, "%s/templates/custom" % p)
      os.rename("%s/branding/olex2" % p, "%s/branding/custom" % p)
    else:
      if os.path.exists(p):
        print("The location %s already exists. No files have been copied" % p)
      else:
        print("This path %s should exist, but does not." % p)
        return
    olx.Shell(p)

  def get_customisation_path(self, custom_name=None):
    if custom_name:
      p = self.p_path + custom_name
      if os.path.exists(p):
        self.customisation_path = p
      else:
        self.customisation_path = None
    else:
      self.customisation_path = None

def make_new_plugin(name, overwrite=False):
  plugin_base = "%s/util/pyUtil/PluginLib/" % OV.BaseDir()
  path = "%s/plugin-%s" % (plugin_base, name)
  xld = "%s/plugins.xld" % OV.BaseDir()

  if os.path.exists(path):
    if overwrite:
      import shutil
      shutil.rmtree(path)
    else:
      print("This plugin already exists.")
      return
  if not os.path.exists(path):
    try:
      os.mkdir(path)
    except:
      print("Failed to make folder %s" % path)
      return

  d = {'name': name,
       'name_lower': name.lower(),
       'plugin_base': plugin_base,
       }
  template_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugin_skeleton.txt')
  py = gui.tools.TemplateProvider.get_template('plugin_skeleton_py', marker='@-@', path=template_src, force=debug) % d

  wFile = open("%(plugin_base)s/plugin-%(name)s/%(name)s.py" % d, 'w')
  wFile.write(py)
  wFile.close()

  phil = gui.tools.TemplateProvider.get_template('plugin_skeleton_phil', marker='@-@', path=template_src, force=debug) % d

  wFile = open("%(plugin_base)s/plugin-%(name)s/%(name_lower)s.phil" % d, 'w')
  wFile.write(phil)
  wFile.close()

  html = gui.tools.TemplateProvider.get_template('plugin_skeleton_html', path=template_src, force=debug) % d
  wFile = open("%(plugin_base)s/plugin-%(name)s/%(name_lower)s.htm" % d, 'w')
  wFile.write(html)
  wFile.close()

  def_t = gui.tools.TemplateProvider.get_template('plugin_skeleton_def', path=template_src, force=debug) % d

  wFile = open("%(plugin_base)s/plugin-%(name)s/def.txt" % d, 'w')
  wFile.write(def_t)
  wFile.close()

  h3_extras = gui.tools.TemplateProvider.get_template('plugin_h3_extras', path=template_src, force=debug) % d

  wFile = open("%(plugin_base)s/plugin-%(name)s/h3-%(name)s-extras.htm" % d, 'w')
  wFile.write(h3_extras)
  wFile.close()

  if not os.path.exists(xld):
    wFile = open(xld, 'w')
    t = r'''
<Plugin
  <%(name)s>
>''' % d
    wFile.write(t)
    wFile.close()
    return

  rFile = open(xld, 'r').read().split()
  if name in " ".join(rFile):
    return
  t = ""
  for line in rFile:
    t += "%s\n" % line
    if line.strip() == "<Plugin":
      t += "<%(name)s>\n" % d
  wFile = open(xld, 'w')
  wFile.write(t)
  wFile.close()

  print("New Plugin %s created. Please restart Olex2" % name)


OV.registerFunction(make_new_plugin, False, 'pt')
