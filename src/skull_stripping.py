from typing import Tuple
from time import time

from pyrobex.robex import robex
import nibabel as nib

def skull_stripping(nib_img) -> Tuple[nib.Nifti1Image, nib.Nifti1Image, float]:
  start_time = time()
  stripped, mask = robex(nib_img)
  processing_time = time() - start_time

  return stripped, mask, processing_time