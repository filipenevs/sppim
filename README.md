## Config Parameters

```py
DEFAULT_GENERAL_CONFIG_PARAMETERS = {
  'SAVE_INTERMEDIATE_STEPS': 'True',
}

DEFAULT_DENOISE_CONFIG_PARAMETERS = {
  'ENABLED': 'True',
  'PATCH_RADIUS': '1',
  'BLOCK_RADIUS': '7',
  'RICIAN': 'True', # False value uses Gaussian as alternative 
  'USE_ANTS': 'True', # False value uses DIPY as alternative
  'NUM_THREADS': '1', # Only for DIPY
  'SHRINK_FACTOR': '1', # Only for ANTs
}

DEFAULT_BIAS_FIELD_CONFIG_PARAMETERS = {
  'ENABLED': 'True',
  'SHRINK_FACTOR': '2',
}
```