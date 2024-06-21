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

DEFAULT_BIAS_FIELD_CONFIG_PARAMETERS = {
  'ENABLED': 'True',
  'SHRINK_FACTOR': '2',
}

class ConfigManager:
  def __init__(self, config_file):
    self.config_file = config_file
    self.config = configparser.ConfigParser()
    self.read_config()

  def read_config(self):
    self.config.read(self.config_file)

  def create_default_config(self):
    self.config['GENERAL'] = DEFAULT_GENERAL_CONFIG_PARAMETERS
    self.config['DENOISE'] = DEFAULT_DENOISE_CONFIG_PARAMETERS
    self.config['BIAS_FIELD_REMOVAL'] = DEFAULT_BIAS_FIELD_CONFIG_PARAMETERS

    with open(self.config_file, 'w') as configfile:
      self.config.write(configfile)

  def get_config_value(self, section, option, default):
    try:
      value = self.config.get(section, option)
    except (configparser.NoSectionError, configparser.NoOptionError):
      return default

    if value == '':
      return default
    if isinstance(default, bool):
      return self.config.getboolean(section, option)
    elif isinstance(default, int):
      return self.config.getint(section, option)
    elif isinstance(default, float):
      return self.config.getfloat(section, option)
    return value