import asyncio
from configparser import ConfigParser
from pydexcom import Dexcom, GlucoseReading
from typing import Optional
from dataclasses import dataclass

credentials = ConfigParser()
credentials.read('credentials.conf')

# TODO: replace print statement with log statements.


@dataclass
class Config:
    username = credentials['Login']['USERNAME']
    password = credentials['Login']['PASSWORD']


class DexcomClock:

    def __init__(self):
        self._dexcom: Optional[Dexcom] = None
        self._blood_glucose: Optional[GlucoseReading] = None
        self.found = False

    async def connect(self):
        """
        Connects to the Dexcom server and sets the "connected" instance
        attribute to True.
        """
        await asyncio.sleep(0)
        await self._call_dexcom()
        await asyncio.sleep(0)

    async def _call_dexcom(self):
        print("Calling Dexcom...")
        await asyncio.sleep(0)
        self._dexcom = Dexcom(Config.username, Config.password)
        print('Connected with Dexcom!')
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
        return self._blood_glucose.value

    async def message(self):
        while self.found is False:
            await asyncio.sleep(0)
            print('Waiting for response.')
            await asyncio.sleep(0)
            print('')

    async def async_loop(self):
        await asyncio.gather(self.message(), self.connect())

    def start_async_loop(self):
        asyncio.run(self.async_loop())
        print('Done with async')
