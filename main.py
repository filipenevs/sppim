import os
import sys

import SimpleITK as sitk

from src.config import ConfigManager
from src.skull_stripping import skull_stripping
from src.denoise import denoise_image
from src.image_io import load_nib_image, save_nib_image, save_sitk_image, load_sitk_image
from src.bias_field import remove_bias_field
from src.utils import log, bcolors, normalize_dir_path, list_files_in_directory
from src.file_name import FileName, basenames

def proccess_image(image_file_name, output_dir, config_manager):
  log(f"\n# {image_file_name}", bcolors.OKCYAN)

  file_name = FileName(image_file_name, output_dir)

  # Loading
  log("> Loading Image")
  work_image = load_nib_image(image_file_name)
  log("> Image Loaded", bcolors.OKGREEN, True)

  # Skull Stripping (NIB)
  work_image_stripped_fname = file_name.get_output_fname(basenames.STRIPPED)
  work_image_mask_fname = file_name.get_output_fname(basenames.MASK)

  if not os.path.exists(work_image_stripped_fname) or not os.path.exists(work_image_mask_fname):
    log("> Running Image Skull Stripping")
    work_image, mask_image, time = skull_stripping(work_image)
    log(f"> Image Skull Stripping Finished (took {time:.2f}s)", bcolors.OKGREEN, True)

    save_nib_image(work_image, work_image_stripped_fname)
    save_nib_image(mask_image, work_image_mask_fname)
  else:
    log("> Image Skull Stripping Already Taken", bcolors.OKGREEN)
    mask_image = load_nib_image(work_image_mask_fname)

  # Denoising (NIB)
  work_image_denoised_fname = file_name.get_output_fname(basenames.DENOISED)

  if not os.path.exists(work_image_denoised_fname):
    log("> Running Image Denoising")
    work_image, time = denoise_image(work_image, mask_image, config_manager)
    log(f"> Image Denoising finished (took {time:.2f}s)", bcolors.OKGREEN, True)

    save_nib_image(work_image, work_image_denoised_fname)
  else:
    log("> Image Denoising Already Taken", bcolors.OKGREEN)

  # Bias field removal (SITK)
  work_image_biasfielded_fname = file_name.get_output_fname(basenames.BIASFIELDED)

  if not os.path.exists(work_image_biasfielded_fname):
    log("> Running Bias Field Removal")

    work_image = load_sitk_image(work_image_denoised_fname, sitk.sitkFloat32)
    mask_image = load_sitk_image(work_image_mask_fname, sitk.sitkUInt8)

    work_image, time = remove_bias_field(work_image, mask_image, config_manager)

    log(f"> Bias Field Removed (took {time:.2f}s)", bcolors.OKGREEN, True)

    save_sitk_image(work_image, work_image_biasfielded_fname)
  else:
    log("> Bias Field Already Removed", bcolors.OKGREEN)

def main(input_dir, output_dir, config_path):
  # Config
  log("> Loading Config")
  config_manager = ConfigManager(config_path)
  log("> Config Loaded", bcolors.OKGREEN, True)

  # Input Files
  log("> Reading Input Directory")
  extensions = config_manager.get_config_value('GENERAL', 'EXTENSIONS', default=['.nii', '.nii.gz'])
  input_images = list_files_in_directory(input_dir, extensions)
  log("> Input Directory Readed", bcolors.OKGREEN, True)

  for path in input_images:
    proccess_image(path, output_dir, config_manager)

if __name__ == "__main__":
  script_dir = os.path.dirname(__file__)
  config_path = os.path.join(script_dir, "config.txt")

  if len(sys.argv) == 2 and sys.argv[1] == "--generate-config":
    config_manager = ConfigManager(config_path)
    config_manager.create_default_config()
    print(f"Default configuration file created at {config_path}.\nPlease edit it with appropriate values.")
    sys.exit(0)

  if len(sys.argv) != 3:
    print("Usage: python main.py <INPUT_DIR> <OUTPUT_DIR>")
    print("Or to generate a default config file: python main.py --generate-config")
    sys.exit(1)

  if not os.path.exists(config_path):
    print(f"No configuration file found at {config_path}.\nPlease run 'python3 main.py --generate-config' to create a default config file.")
    sys.exit(1)

  input_dir = os.path.abspath(normalize_dir_path(sys.argv[1]))
  output_dir = os.path.abspath(normalize_dir_path(sys.argv[2]))

  main(input_dir, output_dir, config_path)