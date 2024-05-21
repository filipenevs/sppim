import configparser

DEFAULT_GENERAL_CONFIG_PARAMETERS = {
  'SAVE_INTERMEDIATE_STEPS': 'False',
}

DEFAULT_DENOISE_CONFIG_PARAMETERS = {
  'ENABLED': 'True',
  'PATCH_RADIUS': '1',
  'BLOCK_RADIUS': '7',
  'RICIAN': 'True',
  'NUM_THREADS': '',
}

DEFAULT_DENOISE_ATLAS_CONFIG_PARAMETERS = {
  'ENABLED': 'False',
  'PATCH_RADIUS': '',
  'BLOCK_RADIUS': '',
  'RICIAN': '',
  'NUM_THREADS': '',
}

DEFAULT_BIAS_FIELD_CONFIG_PARAMETERS = {
  'ENABLED': 'True',
  'SHRINK_FACTOR': '2',
}

def read_config(config_file):
  config = configparser.ConfigParser()
  config.read(config_file)
  return config

def create_default_config(config_path):
  config = configparser.ConfigParser()
  config['GENERAL'] = DEFAULT_GENERAL_CONFIG_PARAMETERS
  config['DENOISE'] = DEFAULT_DENOISE_CONFIG_PARAMETERS
  config['DENOISE_ATLAS'] = DEFAULT_DENOISE_ATLAS_CONFIG_PARAMETERS
  config['BIAS_FIELD_REMOVAL'] = DEFAULT_BIAS_FIELD_CONFIG_PARAMETERS

  with open(config_path, 'w') as configfile:
    config.write(configfile)

def get_config_value(config, section, option, default):
  value = config.get(section, option)

  if value == '':
    return default
  if isinstance(default, bool):
    return config.getboolean(section, option)
  elif isinstance(default, int):
    return config.getint(section, option)
  elif isinstance(default, float):
    return config.getfloat(section, option)
  return value