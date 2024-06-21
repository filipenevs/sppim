import os
import sys
from time import time

import SimpleITK as sitk
import itk

from src.config import ConfigManager
from src.skull_stripping import skull_stripping
# from src.denoise import denoise_image
from src.image_io import load_nib_image, save_nib_image, save_sitk_image, load_sitk_image, save_nib_image_to_tempfile, save_sitk_image_to_tempfile, load_itk_image, save_itk_image, save_itk_image_to_tempfile, cleanup_tempfile
from src.bias_field import remove_bias_field
from src.utils import log, bcolors, normalize_dir_path
from src.orientation import sync_images_orientation

def main(mri_path, output_dir, config_path):
  # Config
  log("> Loading Config")
  config_manager = ConfigManager(config_path)
  # config = read_config(config_path)
  log("> Config Loaded", bcolors.OKGREEN, True)

  save_stepwise = config_manager.get_config_value('GENERAL', 'SAVE_INTERMEDIATE_STEPS', default=False)
  print(save_stepwise)
  return


  # Loading
  log("> Loading Images")
  original_work_image = load_itk_image(mri_path)
  log("> Images Loaded", bcolors.OKGREEN, True)

  if save_stepwise:
    save_itk_image(original_work_image, f'./{output_dir}/1.ORIGINAL_ORIENTED.nii')

  # Skull Stripping (NIB)
  temp_path_original = save_itk_image_to_tempfile(original_work_image)
  original_work_image = load_nib_image(temp_path_original)

  log("> Running Original Image Skull Stripping")
  original_work_image, original_mask, time = skull_stripping(original_work_image)
  log(f"> Original Image Skull Stripping finished (took {time:.2f}s)", bcolors.OKGREEN, True)

  if save_stepwise:
    save_nib_image(original_work_image, f'./{output_dir}/2.ORIGINAL_STRIPPED.nii')
    save_nib_image(original_mask, f'./{output_dir}/2.ORIGINAL_MASK.nii')

  cleanup_tempfile(temp_path_original)

  # Denoising (NIB)
  original_denoising_enabled = config_manager.get_config_value('DENOISE', 'ENABLED', default=True)
  if original_denoising_enabled:
    log("> Running Original Image Denoising")
    original_work_image, time = denoise_image(original_work_image, original_mask)
    log(f"> Original Image Denoising finished (took {time:.2f}s)", bcolors.OKGREEN, True)

  if save_stepwise:
    save_nib_image(original_work_image, f'./{output_dir}/3.ORIGINAL_DENOISED.nii')

  # Bias field removal (SITK)
  bias_field_removal_enabled = config_manager.get_config_value('BIAS_FIELD_REMOVAL', 'ENABLED', default=True)
  if bias_field_removal_enabled:
    log("> Running Bias Field Removal")
    temp_path_original = save_nib_image_to_tempfile(original_work_image)
    temp_path_original_mask = save_nib_image_to_tempfile(original_mask)

    original_work_image = load_sitk_image(temp_path_original, sitk.sitkFloat32)
    original_mask = load_sitk_image(temp_path_original_mask, sitk.sitkUInt8)

    original_work_image, time = remove_bias_field(original_work_image, original_mask)

    log(f"> Bias Field Removed (took {time:.2f}s)", bcolors.OKGREEN, True)

    if save_stepwise:
      save_sitk_image(original_work_image, f'./{output_dir}/4.ORIGINAL_BIASFIELDED.nii')

    cleanup_tempfile(temp_path_original)
    cleanup_tempfile(temp_path_original_mask)

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
    print(f"No configuration file found at {config_path}. Please run 'python main.py --generate-config' to create a default config file.")
    sys.exit(1)

  input_dir = normalize_dir_path(sys.argv[1])
  output_dir = normalize_dir_path(sys.argv[2])
  
  main(input_dir, output_dir, config_path)