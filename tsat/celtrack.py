import requests
from typing import Optional, List
from dataclasses import dataclass, field
import ephem
from datetime import datetime
import numpy as np


@dataclass
class SatData:
    name: str
    tle_line1: str
    tle_line2: str

    def __repr__(self) -> str:
        return f"{self.name}/{self.tle_line1}/{self.tle_line2}"


@dataclass
class SatLoc:
    when: datetime
    az: float
    el: float


@dataclass
class SatPos:
    name: str
    positions: List[SatLoc] = field(default_factory=list)


class Satellites:
    def __init__(self):
        self._names = []
        self._data = []

    def find(self, wanted_sat: str) -> Optional[SatData]:
        if wanted_sat in self._names:
            for s in self._data:
                if s.name == wanted_sat:
                    return s
        else:
            return None

    def reset(self):
        self._names = []
        self._data = []

    def append(self, sat_data: SatData) -> int:
        self._data.append(sat_data)
        self._names.append(sat_data.name)
        return len(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def getname(self, pos: int) -> str:
        return self._names[pos]

    def getsat(self, pos: int) -> SatData:
        return self._data[pos]


class Celtrack:

    def __init__(self):
        datasets = ['http://celestrak.com/NORAD/elements/active.txt',
                    'http://celestrak.com/NORAD/elements/weather.txt',
                    'http://celestrak.com/NORAD/elements/amateur.txt']
        self._sats = Satellites()

        # Setup lat long of telescope
        self.home = ephem.Observer()
        self.home.lat = np.deg2rad(15.15)
        self.home.long = np.deg2rad(120.70)
        self.home.date = datetime.now()

        # Min Elevation sat 10 Degrees
        self.min_ele = 10

    @property
    def minele(self):
        return self.min_ele

    @property
    def location(self):
        return self.home

    @property
    def satellites(self):
        return self._sats

    def get(self, sat_url):
        r = requests.get(sat_url)
        if r.status_code == 200:
            data = r.content.decode('utf-8')
            return data

    def read_tle_data(self, tle_data: str) -> Optional[Satellites]:
        lines = tle_data.split('\n')
        names = lines[::3]
        tle_line_1s = lines[1::3]
        tle_line_2s = lines[2::3]
        self._sats.reset()
        try:
            for item in range(len(names)):
                lcl_name = names.pop()
                if lcl_name:
                    self._sats.append(SatData(name=lcl_name,
                                              tle_line1=tle_line_1s.pop(),
                                              tle_line2=tle_line_2s.pop()))
        except IndexError as i_error:
            pass
        return self._sats