import os

class Util:
    @staticmethod
    def get_conf_dir():
        return os.path.expanduser('~/.zwift-to-garmin/')

    @staticmethod
    def create_environment():
        """
        Create the environment like the config directory
        """
        config_dir = Util.get_conf_dir()
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            self.logger.info("Created config directory: {}".format(config_dir))
        if not os.path.exists(config_dir + '.garth/'):
            os.makedirs(config_dir + '.garth/')
            self.logger.info("Created garth config directory: {}".format(config_dir + '.garth/'))