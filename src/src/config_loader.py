import yaml

def load_config(config_path='frequency_config.yaml'):
    with open(config_path) as f:
        config = yaml.safe_load(f)['frequency_patterns']
    return config
