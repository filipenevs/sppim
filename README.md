# Medical Image Pre-processing Pipeline

This project provides a pre-processing pipeline for MRI images. The pipeline includes the following steps:

1. Skull Stripping
2. Denoising
3. Bias Field Removal

## Table of Contents

- Prerequisites :construction:	
- [Installation](#instalation)
- [Configuration](#configuration)
  - [Config Parameters](#config-parameters)
- [Usage](#usage)

## Instalation

To install the required libraries, run:

```
$ pip3 install -r requirements.txt
```

## Configuration

To generate the configuration file, run the following command:

```
$ python3 main.py --generate-config
```

### Config Parameters

```py
DEFAULT_GENERAL_CONFIG_PARAMETERS = {
  'EXTENSIONS': '.nii, .nii.gz'
}

DEFAULT_DENOISE_CONFIG_PARAMETERS = {
  'PATCH_RADIUS': '1',
  'BLOCK_RADIUS': '7',
  'RICIAN': 'True', # False value uses Gaussian as alternative 
  'USE_ANTS': 'True', # False value uses DIPY as alternative
  'NUM_THREADS': '1', # Only for DIPY
  'SHRINK_FACTOR': '1', # Only for ANTs
}

DEFAULT_BIAS_FIELD_CONFIG_PARAMETERS = {
  'SHRINK_FACTOR': '2',
}
```

## Usage

To run the pre-processing pipeline, use the following command:

```
$ python3 main.py <input_directory> <output_directory>
```

Replace `<input_directory>` with the path to your input MRI images and `<output_directory>` with the path where you want to save the processed images.

### Example

```
$ python3 main.py ./inputDir ./outDir
```