import itk

def get_nifti_image_orientation(itk_img):
  direction_matrix = itk_img.GetDirection()

  orientation = ""

  if direction_matrix(0,0) > 0:
    orientation += "R"
  else:
    orientation += "L"

  if direction_matrix(1,1) > 0:
    orientation += "A"
  else:
    orientation += "P"
  if direction_matrix(2,2) > 0:
    orientation += "I"
  else:
    orientation += "S"

  return orientation

def orient_image(itk_img, orient="LPI"):
  ImageType = type(itk_img)

  ITK_COORDINATE_Right     = 2
  ITK_COORDINATE_Left      = 3
  ITK_COORDINATE_Posterior = 4
  ITK_COORDINATE_Anterior  = 5
  ITK_COORDINATE_Inferior  = 8
  ITK_COORDINATE_Superior  = 9
  ITK_COORDINATE_PrimaryMinor   = 0
  ITK_COORDINATE_SecondaryMinor = 8
  ITK_COORDINATE_TertiaryMinor  = 16

  match orient:
    case "RAS":
      itk_coords =  ( ITK_COORDINATE_Right     << ITK_COORDINATE_PrimaryMinor   ) \
                  + ( ITK_COORDINATE_Anterior  << ITK_COORDINATE_SecondaryMinor ) \
                  + ( ITK_COORDINATE_Superior  << ITK_COORDINATE_TertiaryMinor  )
    case "RAI":
      itk_coords =  ( ITK_COORDINATE_Right     << ITK_COORDINATE_PrimaryMinor   ) \
                  + ( ITK_COORDINATE_Anterior  << ITK_COORDINATE_SecondaryMinor ) \
                  + ( ITK_COORDINATE_Inferior  << ITK_COORDINATE_TertiaryMinor  )
    case "LPS":
      itk_coords =  ( ITK_COORDINATE_Left      << ITK_COORDINATE_PrimaryMinor   ) \
                  + ( ITK_COORDINATE_Posterior << ITK_COORDINATE_SecondaryMinor ) \
                  + ( ITK_COORDINATE_Superior  << ITK_COORDINATE_TertiaryMinor  )
    case "LPI":
      itk_coords =  ( ITK_COORDINATE_Left      << ITK_COORDINATE_PrimaryMinor   ) \
                  + ( ITK_COORDINATE_Posterior << ITK_COORDINATE_SecondaryMinor ) \
                  + ( ITK_COORDINATE_Inferior  << ITK_COORDINATE_TertiaryMinor  )
    case _:
      print("Orientation Not Supported.")
      exit

  filter = itk.OrientImageFilter[ImageType, ImageType].New( itk_img )
  filter.UseImageDirectionOn()
  filter.SetDesiredCoordinateOrientation( itk_coords )
  filter.Update()
  return filter.GetOutput()

def sync_images_orientation(fix_itk_img, mov_itk_image):
  mov_img_result = orient_image(mov_itk_image, get_nifti_image_orientation(fix_itk_img))
  mov_img_result.SetOrigin(fix_itk_img.GetOrigin())
  return mov_img_result