import os, site, configparser

KEEPER_CONTRACTS = 'keeper-contracts'


def load_config_section(file_path, section):
    try:
        assert file_path and os.path.exists(file_path), 'config file_path is required.'
        config = parse_config(file_path, section)
        return config
    except Exception as err:
        # TODO: replace Exception with custom error class
        raise Exception("You should provide a valid config: %s" % str(err))



def parse_config(file_path, section):
    """Loads the configuration file given as parameter"""
    config_parser = configparser.ConfigParser()
    config_parser.read(file_path)
    config_dict = {}
    options = config_parser.options(section)
    for option in options:
        try:
            config_dict[option] = config_parser.get(section, option)
            if config_dict[option] == -1:
                print("skip: %s" % option)
        except Exception as err:
            print("exception on %s!" % option)
            config_dict[option] = None
    return config_dict


def get_contracts_path(conf):
    try:
        if 'contracts.folder' in conf:
            return conf['contracts.folder']
        elif os.getenv('VIRTUAL_ENV') is not None:
            return "%s/contracts" % (os.getenv('VIRTUAL_ENV'))
        else:
            return "%s/contracts" % site.getsitepackages()[0]
    except Exception as e:
        return e