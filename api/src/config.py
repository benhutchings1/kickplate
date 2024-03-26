import configparser as cfgparse
from src.error_handling import CustomError, HttpCodes
from src.logger import Loggers, LoggingLevel

# Config location
CONFIG_PATH = "config/connection.ini"

class __Config:
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
        
        # Auth config URLs
        self.__meta_dict["auth"]["open_id_config_url"] = f"https://login.microsoftonline.com/{self.get('auth', 'tenant_id')}\
            /v2.0/.well-known/openid-configuration"
        self.__meta_dict["auth"]["issuer_url"] = f"https://sts.windows.net/{self.get('auth', 'tenant_id')}/"
        self.__meta_dict["auth"]["audience"] = f"api://{self.get('auth', 'client_id')}"

    
    def get(self, section:str, key:str) -> str:
        '''Given section and key, get from metadict'''
        # Check for section
        if section in self.__meta_dict:
            # Check for key
            if key in self.__meta_dict[section]:
                return self.__meta_dict[section][key]
        raise CustomError(
            error_code=HttpCodes.INTERNAL_SERVER_ERROR,
            logging_message=f"Error getting config option section: {section} key: {key}",
            logging_level=LoggingLevel.WARNING
        )
        
# Load on app start           
config = __Config()
 