import os
import sys
from time import time

import SimpleITK as sitk
import itk

from src.config import read_config, create_default_config, get_config_value
from src.skull_stripping import skull_stripping
from src.denoise import denoise_image
from src.image_io import load_nib_image, save_nib_image, save_sitk_image, load_sitk_image, save_nib_image_to_tempfile, save_sitk_image_to_tempfile, load_itk_image, save_itk_image, save_itk_image_to_tempfile, cleanup_tempfile
from src.bias_field import remove_bias_field
from src.utils import log, bcolors, normalize_dir_path
from src.orientation import sync_images_orientation
# from preprocessing import preprocess_image

def main(mri_path, atlas_path, output_dir, config_path):
  # Config
  log("> Loading Config")
  config = read_config(config_path)
  log("> Config Loaded", bcolors.OKGREEN, True)

  save_stepwise = get_config_value(config, 'GENERAL', 'SAVE_INTERMEDIATE_STEPS', default=False)

  # Loading
  log("> Loading Images")
  original_work_image = load_itk_image(mri_path)
  atlas_work_image = load_itk_image(atlas_path)
  log("> Images Loaded", bcolors.OKGREEN, True)

  # Orienting (ITK)
  log("> Orienting Atlas Image")
  atlas_work_image = sync_images_orientation(original_work_image, atlas_work_image)
  log("> Atlas Oriented", bcolors.OKGREEN, True)

  if save_stepwise:
    save_itk_image(original_work_image, f'./{output_dir}/1.ORIGINAL_ORIENTED.nii')
    save_itk_image(atlas_work_image, f'./{output_dir}/1.ATLAS_ORIENTED.nii')

  # Skull Stripping (NIB)
  temp_path_original = save_itk_image_to_tempfile(original_work_image)
  temp_path_atlas = save_itk_image_to_tempfile(atlas_work_image)

  original_work_image = load_nib_image(temp_path_original)
  atlas_work_image = load_nib_image(temp_path_atlas)

  log("> Running Original Image Skull Stripping")
  original_work_image, original_mask, time = skull_stripping(original_work_image)
  log(f"> Original Image Skull Stripping finished (took {time:.2f}s)", bcolors.OKGREEN, True)

  log("> Running Atlas Image Skull Stripping")
  atlas_work_image, atlas_mask, time = skull_stripping(atlas_work_image)
  log(f"> Atlas Image Skull Stripping finished (took {time:.2f}s)", bcolors.OKGREEN, True)

  if save_stepwise:
    save_nib_image(original_work_image, f'./{output_dir}/2.ORIGINAL_STRIPPED.nii')
    save_nib_image(original_mask, f'./{output_dir}/2.ORIGINAL_MASK.nii')
    save_nib_image(atlas_work_image, f'./{output_dir}/2.ATLAS_STRIPPED.nii')
    save_nib_image(atlas_mask, f'./{output_dir}/2.ATLAS_MASK.nii')

  cleanup_tempfile(temp_path_original)
  cleanup_tempfile(temp_path_atlas)

  # Denoising (NIB)
  original_denoising_enabled = get_config_value(config, 'DENOISE', 'ENABLED', default=True)
  if original_denoising_enabled:
    log("> Running Original Image Denoising")
    original_work_image, time = denoise_image(original_work_image, original_mask)
    log(f"> Original Image Denoising finished (took {time:.2f}s)", bcolors.OKGREEN, True)

  atlas_denoising_enabled = get_config_value(config, 'DENOISE_ATLAS', 'ENABLED', default=False)
  if atlas_denoising_enabled:
    log("> Running Atlas Image Denoising")
    atlas_work_image, time = denoise_image(atlas_work_image, atlas_mask)
    log(f"> Atlas Image Denoising finished (took {time:.2f}s)", bcolors.OKGREEN, True)

  if save_stepwise:
    save_nib_image(original_work_image, f'./{output_dir}/3.ORIGINAL_DENOISED.nii')
    if atlas_denoising_enabled:
      save_nib_image(atlas_work_image, f'./{output_dir}/3.ATLAS_DENOISED.nii')

  # Bias field removal (SITK)
  bias_field_removal_enabled = get_config_value(config, 'BIAS_FIELD_REMOVAL', 'ENABLED', default=True)
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

  # Registration (ITK)
  log("> Running Registration")
  original_work_image = itk.imread('./outDir/4.BIASFIELDED.nii', itk.F)
  original_work_image_mask = itk.imread('./outDir/2.ORIGINAL_MASK.nii', itk.UC)

  atlas_work_image = itk.imread('./outDir/2.ATLAS_STRIPPED.nii', itk.F)
  atlas_work_image_mask = itk.imread('./outDir/2.ATLAS_MASK.nii', itk.UC)

  parameter_object = itk.ParameterObject.New()

  # Composite transformations: rigid -> affine -> deformable
  parameter_map_rigid = parameter_object.GetDefaultParameterMap('rigid')
 
  parameter_object.AddParameterMap(parameter_map_rigid)
  parameter_object.AddParameterFile('parameters/Par0010.affine.txt')
  parameter_object.AddParameterFile('parameters/Par0010.bspline.txt')
  # parameter_object.AddParameterFile('parameters/Par0021_oxford.txt')

  # Call registration function
  #res_img_elx, res_trafo_params = itk.elastix_registration_method(original_work_image, atlas_work_image, parameter_object, number_of_threads=6, fixed_mask= original_work_image_mask, moving_mask=atlas_work_image_mask, log_to_console=True)

  res_img_elx, res_trafo_params = itk.elastix_registration_method(original_work_image, atlas_work_image, parameter_object, number_of_threads=6)

  # log(f"> Registraion finished (took {time:.2f}s)", bcolors.OKGREEN, True)

  # Write image to disk
  itk.imwrite(res_img_elx, f'./{output_dir}/5.REGISTRATION.nii')

if __name__ == "__main__":
  script_dir = os.path.dirname(__file__)
  config_path = os.path.join(script_dir, "config.txt")

  if len(sys.argv) == 2 and sys.argv[1] == "--generate-config":
    create_default_config(config_path)
    print(f"Default configuration file created at {config_path}. Please edit it with appropriate values.")
    sys.exit(0)

  if len(sys.argv) != 4:
    print("Usage: python main.py <MRI_PATH> <ATLAS_PATH> <OUTPUT_DIR>")
    print("Or to generate a default config file: python main.py --generate-config")
    sys.exit(1)

  mri_path = sys.argv[1]
  atlas_path = sys.argv[2]
  output_dir = normalize_dir_path(sys.argv[3])

  if not os.path.exists(config_path):
    print(f"No configuration file found at {config_path}. Please run 'python main.py --generate-config' to create a default config file.")
    sys.exit(1)
  
  main(mri_path, atlas_path, output_dir, config_path)