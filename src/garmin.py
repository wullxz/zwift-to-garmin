import garth
import tempfile
import logging
import time

from io import BytesIO
from garth.exc import GarthException, GarthHTTPError
from zwiftwrapper import ZwiftActivity
from util import Util
from gmail import Gmail

class Garmin:
  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.logger = logging.getLogger('my_app')
    conf_dir = Util.get_conf_dir()
    
    try:
      garth.resume(conf_dir + '/.garth')
      garth.client.username
      self.logger.info("Restored Garmin login. Garmin username: {}".format(garth.client.username))
    except (GarthException, FileNotFoundError) as e:
      garth.login(self.username, self.password, prompt_mfa=lambda: self.get_garmin_code())
      garth.save(conf_dir + '/.garth')
  
  def get_garmin_code(self):
    if Gmail.has_api_token():
      self.logger.info("Trying to read Garmin MFA code from Gmail.")
      gmail = Gmail()
      return gmail.get_garmin_code()
    else:
      return input("Enter Garmin MFA code: ")

  def upload_fitfile(self, fitfile: ZwiftActivity):
    self.logger.info("Uploading activity ID: {}".format(fitfile.activity_id))
    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, 'wb') as f:
      self.logger.info("Writing FIT file to temporary file: {}".format(f.name))
      f.write(fitfile.activity_data)
      f.seek(0)
    with open(tmp.name, 'rb') as f:
      try:
        garth.upload(f)
      except GarthHTTPError as e:
        self.logger.error("Garmin upload failed: {}".format(e))
