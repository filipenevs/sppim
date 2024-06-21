import os
import sys

import SimpleITK as sitk

from src.config import ConfigManager
from src.skull_stripping import skull_stripping
from src.denoise import denoise_image
from src.image_io import load_nib_image, save_nib_image, save_sitk_image, load_sitk_image, save_nib_image_to_tempfile, save_sitk_image_to_tempfile, load_itk_image, save_itk_image, save_itk_image_to_tempfile, cleanup_tempfile
from src.bias_field import remove_bias_field
from src.utils import log, bcolors, normalize_dir_path, list_files_in_directory
from src.orientation import sync_images_orientation

def proccess_image(image_file_name, output_dir, config_manager):
  log(f"\n# {image_file_name}", bcolors.OKCYAN)

  file_name_with_extension = os.path.basename(image_file_name)
  file_name, file_extension = os.path.splitext(file_name_with_extension)

  save_stepwise = config_manager.get_config_value('GENERAL', 'SAVE_INTERMEDIATE_STEPS', default=True)

  # Loading
  log("> Loading Image")
  work_image = load_itk_image(image_file_name)
  log("> Image Loaded", bcolors.OKGREEN, True)

  # Skull Stripping (NIB)
  temp_path_original = save_itk_image_to_tempfile(work_image)
  work_image = load_nib_image(temp_path_original)

  log("> Running Image Skull Stripping")
  work_image, mask_image, time = skull_stripping(work_image)
  log(f"> Image Skull Stripping finished (took {time:.2f}s)", bcolors.OKGREEN, True)

  if save_stepwise:
    save_nib_image(work_image, f'{output_dir}/{file_name}-1_stripped{file_extension}')
    save_nib_image(mask_image, f'{output_dir}/{file_name}-1_mask{file_extension}')

  # Denoising (NIB)
  denoising_enabled = config_manager.get_config_value('DENOISE', 'ENABLED', default=True)
  if denoising_enabled:
    log("> Running Image Denoising")
    work_image, time = denoise_image(work_image, mask_image, config_manager)
    log(f"> Image Denoising finished (took {time:.2f}s)", bcolors.OKGREEN, True)

    if save_stepwise:
      save_nib_image(work_image, f'{output_dir}/{file_name}-2_denoised{file_extension}')

  # Bias field removal (SITK)
  bias_field_removal_enabled = config_manager.get_config_value('BIAS_FIELD_REMOVAL', 'ENABLED', default=True)
  if bias_field_removal_enabled:
    log("> Running Bias Field Removal")
    temp_path_work_image = save_nib_image_to_tempfile(work_image)
    temp_path_mask_image = save_nib_image_to_tempfile(mask_image)

    work_image = load_sitk_image(temp_path_work_image, sitk.sitkFloat32)
    mask_image = load_sitk_image(temp_path_mask_image, sitk.sitkUInt8)

    work_image, time = remove_bias_field(work_image, mask_image, config_manager)

    log(f"> Bias Field Removed (took {time:.2f}s)", bcolors.OKGREEN, True)

    if save_stepwise:
      save_sitk_image(work_image, f'{output_dir}/{file_name}-3_biasfielded{file_extension}')

    cleanup_tempfile(temp_path_work_image)
    cleanup_tempfile(temp_path_mask_image)

def main(input_dir, output_dir, config_path):
  # Config
  log("> Loading Config")
  config_manager = ConfigManager(config_path)
  log("> Config Loaded", bcolors.OKGREEN, True)

  # Input Files
  log("> Reading Input Directory")
  input_images = list_files_in_directory(input_dir)
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