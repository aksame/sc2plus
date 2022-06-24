import argparse
import os
import lib.iso

def execute(parser, args):
  root_dir = 'base'
  output_dir = "build\\root"
  input_iso = 'base\\grseaf.iso'
  output_iso = 'build\\sc2plus.iso'

  if args.extract:
    lib.iso.extract(input_iso, root_dir)
  elif args.rebuild:
    if os.path.exists(output_dir) != True:
      lib.iso.copy_dir(os.path.join(root_dir,"root"), output_dir)
    else:
      print(f'{output_dir} already exists! Rebuilding...')
    lib.iso.patch()
    lib.iso.rebuild(os.path.abspath(output_iso), output_dir)
  elif args.clean:
    lib.iso.clean()
  elif args.olk:
    lib.olk.expand(os.path.abspath('base\\root\\files\\root.olk'), os.path.abspath('mod'))
  elif args.patch:
    lib.olk.replace(os.path.abspath('mod'))
  else:
    parser.parse_args(["-h"])

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Soul Calibur 2 Plus mod builder")
  parser.add_argument("-e", dest="extract", help="Extract files from base ISO", action="store_true")
  parser.add_argument("-o", dest="olk", help="Expand root.olk", action="store_true")
  parser.add_argument("-p", dest="patch", help="Patch root.olk with files in mod\\root folder", action="store_true")
  parser.add_argument("-r", dest="rebuild", help="Copy mod files and rebuild ISO", action="store_true")
  parser.add_argument("-c", dest="clean", help="Remove extracted file directories", action="store_true")
  args = parser.parse_args()

  execute(parser, args)