import nibabel as nib
import SimpleITK as sitk
import itk

IMAGE_SUFFIX = '.nii'

# NIB
def load_nib_image(file_path):
  img = nib.load(file_path)
  return img

def save_nib_image(nib_image, output_path):
  nib.save(nib_image, output_path)

# SITK
def load_sitk_image(file_path, outputPixelType):
  img = sitk.ReadImage(file_path, outputPixelType)
  return img

def save_sitk_image(sitk_image, output_path):
  sitk.WriteImage(sitk_image, output_path)

# ITK
def load_itk_image(file_path):
  img = itk.imread(file_path)
  return img

def save_itk_image(itk_image, output_path):
  itk.imwrite(itk_image, output_path)