import yaml



def get_config_data():
    config_data = {}
    with open("/home/ubuntu/app_tier/config.yaml", "r") as stream:
        try:
            config_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc) 
    return config_data
    