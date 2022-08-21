import asyncio
from configparser import ConfigParser
from pydexcom import Dexcom, GlucoseReading
from typing import Optional
from dataclasses import dataclass
import logging
from collections import namedtuple

GlucoseAndTrend = namedtuple('GlucoseAndTrend', ('glucose_level', 'trend_description'))


logging.basicConfig(level=logging.INFO)

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
        self.found = False

    def connect(self):
        """
        Connects to the Dexcom server and sets the "connected" instance
        attribute to True.
        """
        logging.info("Calling Dexcom...")
        self._dexcom = Dexcom(Config.username, Config.password)
        logging.info('Connected with Dexcom!')
        self.found = True

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
        return GlucoseAndTrend(self._blood_glucose.value, self._blood_glucose.trend_description)

    async def message(self):
        if logging.root.level > logging.INFO:
            return
        while self.found is False:
            await asyncio.sleep(0.2)
            logging.info('Waiting for response.')
            await asyncio.sleep(0.2)
            logging.info('')

    async def async_loop(self):
        await asyncio.gather(
            self.message(),
            asyncio.to_thread(self.connect))

    def start_async_loop(self):
        asyncio.run(self.async_loop())
        logging.info('Done with async')
