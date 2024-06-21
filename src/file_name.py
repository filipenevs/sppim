import os

class basenames:
  STRIPPED = '1_stripped'
  MASK = '1_mask'
  DENOISED = '2_denoised'
  BIASFIELDED = '3_biasfielded'
  

class FileName:
  def __init__(self, original_file_name, output_dir, extensions):
    self.output_dir = output_dir

    file_name_with_extension = os.path.basename(original_file_name)

    for ext in extensions:
      if file_name_with_extension.endswith(ext):
        
        self.file_name = file_name_with_extension[:-len(ext)]
        self.file_extension = ext

  def get_output_fname(self, image_type):
    return f'{self.output_dir}/{self.file_name}-{image_type}{self.file_extension}'