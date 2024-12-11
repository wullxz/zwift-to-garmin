from zwift import Client
import requests
import logging

from fit_tool.fit_file import FitFile
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.profile_type import GarminProduct, Manufacturer
from fit_tool.utils.crc import crc16

logger = logging.getLogger('my_app')
    
class ZwiftActivity:
    def __init__(self, activity_id, activity_data):
        self.activity_id = activity_id
        self.activity_data = activity_data
        self.fitfile = FitFile.from_bytes(self.activity_data)

    def change_manufacturer(self):
        # We have to change the manufacturer and product in both the file id and device info
        device = [f for f in self.fitfile.records if isinstance(f.message, DeviceInfoMessage)][0]
        device.message.manufacturer = Manufacturer.GARMIN
        device.message.product = GarminProduct.EDGE_1030

        fileid = [f for f in self.fitfile.records if isinstance(f.message, FileIdMessage)][0]
        fileid.message.manufacturer = Manufacturer.GARMIN
        fileid.message.product = GarminProduct.EDGE_1030

        self.recalculate_crc()
        return self

    def recalculate_crc(self) -> int:
        crc = 0
        crc = crc16(self.fitfile.header.to_bytes(), crc=crc)
        for record in self.fitfile.records:
            crc = crc16(record.to_bytes(), crc=crc)
        self.fitfile.crc = crc
        return self


class Zwift:
    def __init__(self, username, password):
        self.client = Client(username, password)
        self.profile = self.client.get_profile()
        self.profile.check_player_id()
        self.player_id = self.profile.player_id
        logger.info("Player ID: {}".format(self.player_id))
        self.activity = self.client.get_activity(self.player_id)

    def get_activities(self):
        return self.activity.list()

    def get_activity(self, activity_id: str) -> ZwiftActivity:
        """
        Retrieves the activity record with the given ID from Zwift and downloads
        the associated FIT file.

        :param activity_id: The ID of the activity to retrieve.
        :return: A ZwiftActivity object representing the downloaded activity.
        """
        activity_data = self.activity.get_activity(activity_id)
        fit_file_bucket = activity_data['fitFileBucket']
        fit_file_key = activity_data['fitFileKey']
        fit_file_url = 'https://{}.s3.amazonaws.com/{}'.format(
            fit_file_bucket, fit_file_key)
        raw_fit_data = download_file(fit_file_url)
        return ZwiftActivity(activity_id, raw_fit_data)

def download_file(url):
    resp = requests.get(url)
    if not resp.ok:
        raise RequestException("{} - {}".format(
            resp.status_code, resp.reason))
    return resp.content

class RequestException(BaseException):
    pass
