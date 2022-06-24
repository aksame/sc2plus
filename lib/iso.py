import os
import shutil
from pathlib import Path
from pyisotools.iso import GamecubeISO
from . import olk

# Extracts the ISO to a directory
def extract(input_iso, output_dir):
  print(f'Extracting {input_iso} to {output_dir}')
  src = Path(input_iso).resolve()
  iso = GamecubeISO.from_iso(src)
  iso.extract(output_dir)

# Rebuilds a GC ISO given a folder and a destination
def rebuild(output_iso, iso_dir):
  print(f'Rebuilding {iso_dir} to {output_iso}')
  src = Path(iso_dir).resolve()
  iso = GamecubeISO.from_root(src)
  iso.build(output_iso)

# Copies directory including subfiles
def copy_dir(src_dir, dst_dir):
  print(f'Copying {src_dir} to {dst_dir}')
  shutil.copytree(src_dir, dst_dir)

# Replace certain files
def patch():
  mod_dir = 'mod'
  base_dir = 'base'
  build_dir = 'build\\root'
  mod_sys_dir = os.path.join(mod_dir,"sys")
  build_sys_dir = os.path.join(build_dir,"sys")
  mod_files_dir = os.path.join(mod_dir,"files")
  build_files_dir = os.path.join(build_dir,"files")

  print(f'Replacing files...')
  shutil.copytree(mod_sys_dir, build_sys_dir, dirs_exist_ok=True)

  for fn in os.listdir(mod_files_dir):
    mod_fn = os.path.join(mod_files_dir, fn)
    build_fn = os.path.join(build_files_dir, fn)
    if os.path.isfile(mod_fn):
      shutil.copy(mod_fn, build_fn)
      print(f'Copied {mod_fn} to {build_fn}')

# Deletes extracted contents
def clean():
  base_dir = os.path.abspath('base\\root')
  build_dir = os.path.abspath('build\\root')

  if os.path.exists(base_dir) == True:
    print(f'Deleting {base_dir}...')
    shutil.rmtree(base_dir)
  if os.path.exists(build_dir) == True:
    print(f'Deleting {build_dir}...')
    shutil.rmtree(build_dir)
  print(f'Finished!')
