import os

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

def log(text, color=None, clearLine=False):
  if(clearLine):
    print ("\033[A                             \033[A")

  if color is not None:
    print(f"{color}{text}{bcolors.ENDC}")
  else:
    print(text)

def normalize_dir_path(directory):
  return os.path.normpath(directory)

def list_files_in_directory(directory, extensions):
  files = []
  for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path): 
      file_extension = os.path.splitext(filename)[1]
      if file_extension in extensions:
        files.append(file_path)
  return files