from time import time

import SimpleITK as sitk
import numpy as np

def remove_bias_field(sitk_image, sitk_image_mask) -> np.ndarray:
  start_time = time()

  shrink_factor = 2
  input_img = sitk_image
  input_img = sitk.Cast(input_img, sitk.sitkFloat32)

  input_img = sitk.Shrink( input_img, [ shrink_factor ] * input_img.GetDimension() )
  mask_img  = sitk.Shrink( sitk_image_mask, [ shrink_factor ] * input_img.GetDimension() )
  
  bias_corrector = sitk.N4BiasFieldCorrectionImageFilter()
  
  bias_corrector.Execute( input_img, mask_img )

  log_bias_field = bias_corrector.GetLogBiasFieldAsImage(sitk_image)
  corrected_image_full_resolution = sitk_image / sitk.Exp( log_bias_field )

  corrected_image_full_resolution = sitk.Cast(corrected_image_full_resolution, sitk.sitkUInt16)

  processing_time = time() - start_time

  return corrected_image_full_resolution, processing_time