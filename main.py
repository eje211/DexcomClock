from configparser import ConfigParser
from pydexcom import Dexcom, GlucoseReading
from typing import Optional
from dataclasses import dataclass

credentials = ConfigParser()
credentials.read('credentials.conf')


@dataclass
class Config:
    username = credentials['Login']['USERNAME']
    password = credentials['Login']['PASSWORD']


class DexcomClock:

    def __init__(self):
        self._dexcom: Optional[Dexcom] = None
        self._blood_glucose: Optional[GlucoseReading] = None

    def connect(self):
        """
        Connects to the Dexcom server and sets the "connected" instance
        attribute to True.
        """
        try:
            self._dexcom = Dexcom(Config.username, Config.password)
        except Exception:
            raise

    def update(self):
        """
        Get the latest glucose reading from the associated transmitter.
        Connects first if the instance is not connected.
        :return: the latest glucose reading.
        """
        try:
            return self._update()
        except AttributeError:
            self.connect()
            return self._update()

    def _update(self):
        """
        Gets the latest glucose reading from the associated transmitter
        without connecting first.
        :return: The latest glucose reading.
        """
        self._blood_glucose = self._dexcom.get_current_glucose_reading()
        return self._blood_glucose.value
