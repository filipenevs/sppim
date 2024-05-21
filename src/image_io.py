import tempfile
import os

import nibabel as nib
import SimpleITK as sitk
import itk

IMAGE_SUFFIX = '.nii'

def load_nib_image(file_path):
  img = nib.load(file_path)
  return img

def save_nib_image(nib_image, output_path):
  nib.save(nib_image, output_path)

def save_nib_image_to_tempfile(nib_image):
  with tempfile.NamedTemporaryFile(delete=False, suffix=IMAGE_SUFFIX) as temp:
    temp_name = temp.name
    save_nib_image(nib_image, temp_name)
  return temp_name

###################################################################
###################################################################
###################################################################
###################################################################
###################################################################

def load_sitk_image(file_path, outputPixelType):
  img = sitk.ReadImage(file_path, outputPixelType)
  return img

def save_sitk_image(sitk_image, output_path):
  sitk.WriteImage(sitk_image, output_path)

def save_sitk_image_to_tempfile(sitk_image):
  with tempfile.NamedTemporaryFile(delete=False, suffix=IMAGE_SUFFIX) as temp:
    temp_name = temp.name
    save_sitk_image(sitk_image, temp_name)
  return temp_name

###################################################################
###################################################################
###################################################################
###################################################################
###################################################################

def load_itk_image(file_path):
  img = itk.imread(file_path)
  return img

def save_itk_image(itk_image, output_path):
  itk.imwrite(itk_image, output_path)

def save_itk_image_to_tempfile(itk_image):
  with tempfile.NamedTemporaryFile(delete=False, suffix=IMAGE_SUFFIX) as temp:
    temp_name = temp.name
    itk.imwrite(itk_image, temp_name)
  return temp_name

###################################################################
###################################################################
###################################################################
###################################################################
###################################################################

def cleanup_tempfile(tempfile_path):
  try:
    os.remove(tempfile_path)
  except Exception as e:
    print(f"Erro ao tentar remover o arquivo temporário: {e}")