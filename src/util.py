import logging
import os

class Util:
    @staticmethod
    def get_conf_dir():
        return os.path.expanduser('~/.zwift-to-garmin/')

    @staticmethod
    def get_logger():
        return logging.getLogger('my_app')

    @staticmethod
    def create_environment():
        """
        Create the environment like the config directory
        """
        logger = Util.get_logger()
        config_dir = Util.get_conf_dir()
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            logger.info("Created config directory: {}".format(config_dir))
        #if not os.path.exists(config_dir + '.garth/'):
        #    os.makedirs(config_dir + '.garth/')
        #    logger.info("Created garth config directory: {}".format(config_dir + '.garth/'))
