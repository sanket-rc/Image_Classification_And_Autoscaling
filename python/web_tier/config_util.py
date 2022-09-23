import yaml



def get_config_data():
    config_data = {}
    with open("config.yaml", "r") as stream:
        try:
            config_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc) 
    return config_data
    