import os
import sys
import logging

from zwiftwrapper import Zwift
from database import Database
from pprint import pformat
from garmin import Garmin
from util import Util

class App:
    def __init__(self):
        # Set up logging
        self.logger = logging.getLogger('my_app')
        self.logger.setLevel(logging.INFO)
        Util.create_environment()

        z_username = os.environ.get("ZWIFT_USERNAME")
        z_password = os.environ.get("ZWIFT_PASSWORD")

        g_username = os.environ.get("GARMIN_USERNAME")
        g_password = os.environ.get("GARMIN_PASSWORD")

        if not z_username or not z_password:
            logging.error("Missing environment variables. Please set ZWIFT_USERNAME and ZWIFT_PASSWORD.")
            sys.exit(1)

        if not g_username or not g_password:
            logging.error("Missing environment variables. Please set GARMIN_USERNAME and GARMIN_PASSWORD.")
            sys.exit(1)

        self.zwift = Zwift(z_username, z_password)
        self.garmin = Garmin(g_username, g_password)
        self.db = Database()


    def process_activity(self, activity):
        if self.db.contains(activity['id']):
            self.logger.info("Skipping activity ID: {}".format(activity['id']))
            return
        self.logger.info("Working on activity ID: {}".format(activity['id']))
        fitfile = self.zwift.get_activity(activity['id'])
        fitfile.change_manufacturer()
        fitfile.fitfile.to_file("{}.fit".format(activity['id']))
        
        self.garmin.upload_fitfile(fitfile)

        self.db.add(activity['id'])



    def run(self):
        """
        Main program entry point
        :return:
        """

        while True:
            self.logger.info("Starting Zwift data worker")

            activities = self.zwift.get_activities()

            for activity in activities:
                #logger.info("Processing activity:\n{}".format(pformat(activity, indent=4)))
                self.process_activity(activity)
            time.sleep(3600)

if __name__ == "__main__":
    app = App()
    app.run()
