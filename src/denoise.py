from time import time

import nibabel as nib
from dipy.denoise.nlmeans import nlmeans
from dipy.denoise.noise_estimate import estimate_sigma
import ants

def extract_fdata_from_images(*nib_images):
  images_data = tuple(img.get_fdata() for img in nib_images)
  return images_data

def denoise_image_dipy(img_data, mask_data, config):
  sigma = estimate_sigma(img_data, N=32)

  denoised_data = nlmeans(
    img_data,
    mask=mask_data,
    sigma=sigma,
    patch_radius=config['patch_radius'],
    block_radius=config['block_radius'],
    rician=config['rician'],
    num_threads=config['num_threads'])

  return denoised_data

def denoise_image_ants(img_data, mask_data, config):
  ants_img = ants.from_numpy(img_data)
  ants_mask = ants.from_numpy(mask_data)

  noise_model = "Rician" if config['rician'] else "Gaussian"
    
  denoised_ants_img = ants.denoise_image(
    image=ants_img,
    shrink_factor=config['shrink_factor'],
    mask=ants_mask,
    p=config['patch_radius'],
    r=config['block_radius'],
    noise_model=noise_model)

  denoised_data = denoised_ants_img.numpy()

  return denoised_data

def denoise_image(work_img, mask_image, config_manager):
  start_time = time()

  image_data, mask_data = extract_fdata_from_images(work_img, mask_image)

  use_ants = config_manager.get_config_value('DENOISE', 'USE_ANTS', default=True)

  denoise_params = {
    'rician': config_manager.get_config_value('DENOISE', 'RICIAN', default=True),
    'patch_radius': config_manager.get_config_value('DENOISE', 'PATCH_RADIUS', default=7),
    'block_radius': config_manager.get_config_value('DENOISE', 'BLOCK_RADIUS', default=1),
    'num_threads': config_manager.get_config_value('DENOISE', 'NUM_THREADS', default=1),
    'shrink_factor': config_manager.get_config_value('DENOISE', 'SHRINK_FACTOR', default=1)
  }

  denoise_function = denoise_image_ants if use_ants else denoise_image_dipy
  denoised_data = denoise_function(image_data, mask_data, denoise_params)

  denoised_image = nib.Nifti1Image(denoised_data, work_img.affine, work_img.header)

   # normalized_denoised_data = normalize_image(denoised_data)
  # denoised_image = nib.Nifti1Image(normalized_denoised_data, work_img.affine, work_img.header)

  processing_time = time() - start_time

  return denoised_image, processing_time