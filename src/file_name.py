import os

class basenames:
  STRIPPED = '1_stripped'
  MASK = '1_mask'
  DENOISED = '2_denoised'
  BIASFIELDED = '3_biasfielded'
  

class FileName:
  def __init__(self, original_file_name, output_dir):
    self.output_dir = output_dir

    file_name_with_extension = os.path.basename(original_file_name)
    file_name, file_extension = os.path.splitext(file_name_with_extension)

    self.file_name = file_name
    self.file_extension = file_extension

  def get_output_fname(self, image_type):
    return f'{self.output_dir}/{self.file_name}-{image_type}{self.file_extension}'