from time import time
from typing import Tuple

import nibabel as nib
from dipy.denoise.nlmeans import nlmeans
from dipy.denoise.noise_estimate import estimate_sigma

def denoise_image(nib_image, nib_image_mask) -> Tuple[nib.Nifti1Image, float]:
  start_time = time()

  nib_image_array = nib_image.get_fdata()
  nib_image_mask_array = nib_image_mask.get_fdata()

  sigma = estimate_sigma(nib_image_array, N=32)

  denoised_array = nlmeans(nib_image_array, sigma=sigma, mask=nib_image_mask_array, patch_radius=1, block_radius=7, rician=True)

  denoised_image = nib.Nifti1Image(denoised_array, nib_image.affine, nib_image.header)

  processing_time = time() - start_time

  return denoised_image,processing_time