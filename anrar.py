#!/usr/bin/python

"""
Extracts all .rar files in the current directory.
"""

import argparse, os, re, subprocess

class Verbosity :
  QUIET = 0
  ERRS_ONLY = 1
  FULL = 2

def get_command_line_args() :
  """ Parses and returns command line arguments """
  parser = argparse.ArgumentParser(
    description='Extracts all rar files in the current directory')
  parser.add_argument('-d', '--delete-files', action='store_true',
    help='delete .rar files after succesful extraction (default is to keep them)')
  parser.add_argument('-i', '--interactive', action='store_true',
    help='enables interactive mode, where unrar queries must be responded to with y/n')
  parser.add_argument('-p', '--password', action='store',
    help='the password required to extract files') 
  parser.add_argument('-v', '--verbosity', action='store',
    default=2, type=int, choices=[Verbosity.QUIET, Verbosity.ERRS_ONLY, Verbosity.FULL],
    help='verbosity of output. 0 for silence, 1 for errors only, 2 for full output')
  parser.add_argument('--version', action='version', version='anrar 1.0')

  return parser.parse_args()

def get_file_parts_list() :
  """
  Returns a list of lists of file parts for each file to extract.
  Example: If the files are foo.part1.rar, foo.part2.rar, bar.rar, this returns
  [['foo.part1.rar', 'foo.part2.rar'], ['bar.rar']]
  """
  files_to_parts = {}
  files = os.listdir('.')
  for file in files :
    if file.endswith('.rar') :
      # For each file that contains part1, part2, etc, strip that from
      # the filename, and we can then identify files whose names match
      # after the part has been removed
      removed_parts = re.sub('part\d+', '', file)
      files_to_parts.setdefault(removed_parts, []).append(file)
  return files_to_parts.values()

def get_file_to_unrar(file_list) :
  """
  Given a list of .rar parts for the same file, return the filename that
  will be passed to unrar for extraction
  """
  if not file_list :
    raise Exception('No files to extract')
  elif len(file_list) == 1 :
    return file_list[0]
  else :
    # Find part1, and unrar it
    for file in file_list :
      if file.find('part1') >= 0 :
        return file
  raise Exception('No files to extract')

def build_unrar_command(file_list, args) :
  """ Build the command to pass to unrar """
  to_unrar = get_file_to_unrar(file_list)

  command = ['unrar']
  if args.verbosity <= Verbosity.ERRS_ONLY :
    command.append('-idq')
  if not args.interactive :
    command.append('-y')
  if args.password :
    command.append('-p' + args.password)
  command.extend(['x', to_unrar])
  
  return command

def extract(file_list, args) :
  """ Perform the extraction on a list of files """
  command = build_unrar_command(file_list, args)
  ret = subprocess.call(command)
  if ret :
    if args.verbosity >= Verbosity.ERRS_ONLY :
      print 'Failed to unrar:', file_list
  else :
    if args.delete_files :
      # Delete rar files,
      for file in file_list :
        os.remove(file)

def main() :
  args = get_command_line_args()
  for file_list in get_file_parts_list() :
    extract(file_list, args)

if __name__ == '__main__' :
  main()
