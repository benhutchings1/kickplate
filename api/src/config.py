import configparser as cfgparse
from src.error_handling import CustomError, HttpCodes

# Config location
CONFIG_PATH = "config/connection.ini"

class Config:
    """
    Class to retrieve config values from CONFIG_PATH file
    """
    def __init__(self):
        """
        Reads in config values and loads into internal meta dictionary to be searched
        """
        # Read in config
        cfg = cfgparse.ConfigParser()
        cfg.read(CONFIG_PATH)
        
        # Initialise metadict
        self.__meta_dict = {}
        
        # fill metadict
        for section in cfg.sections():
            self.__meta_dict[section] = {}
            for key in cfg[section].keys():
                self.__meta_dict[section][key] = cfg[section][key]

        # Perform post init work
        self.__post_init__()
            
    def __post_init__(self):
        # Make compound keys
        for section in ["workflow", "execgraph"]:
            self.__meta_dict[section]["api_version"] = \
                self.__meta_dict[section]["group"] + "/" + self.__meta_dict[section]["version"]

    
    def get(self, section:str, key:str) -> str:
        # Check for section
        if section in self.__meta_dict:
            # Check for key
            if key in self.__meta_dict[section]:
                return self.__meta_dict[section][key]
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error getting config option section: {section} key: {key}"
        )
        
# Load on app start           
config = Config()
 