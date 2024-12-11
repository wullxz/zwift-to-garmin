import garth
import tempfile
import logging

from io import BytesIO
from garth.exc import GarthException, GarthHTTPError
from zwiftwrapper import ZwiftActivity

class Garmin:
  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.logger = logging.getLogger('my_app')
    
    try:
      garth.resume('~/.garth')
      garth.client.username
      self.logger.info("Restored Garmin login. Garmin username: {}".format(garth.client.username))
    except (GarthException, FileNotFoundError) as e:
      garth.login(self.username, self.password, prompt_mfa=lambda: input("Enter MFA Code: "))
      garth.save('~/.garth')

  def upload_fitfile(self, fitfile: ZwiftActivity):
    self.logger.info("Uploading activity ID: {}".format(fitfile.activity_id))
    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, 'wb') as f:
      self.logger.info("Writing FIT file to temporary file: {}".format(f.name))
      f.write(fitfile.fitfile.to_bytes())
      f.seek(0)
    with open(tmp.name, 'rb') as f:
      try:
        garth.upload(f)
      except GarthHTTPError as e:
        self.logger.error("Garmin upload failed: {}".format(e))
