from unittest import TestCase
from datetime import datetime, timedelta
from unittest.mock import patch
from tsat import Celtrack, SatData, Satellites, SatLoc, SatPos
from freezegun import freeze_time
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
import ephem
import numpy as np


@freeze_time("2019-10-2 08:15")
class TestCeltrack(TestCase):
    weather = """NOAA 1 [-]
1 04793U 70106A   19274.83132212 -.00000026  00000-0  11558-3 0  9994
2 04793 101.6945 341.9842 0032027  83.1238  23.8796 12.53991542233544
NOAA 2 (ITOS-D) [-]
1 06235U 72082A   19274.92139816 -.00000042  00000-0  18102-4 0  9990
2 06235 101.8085 240.7208 0003878 167.3603 255.8895 12.53118736148020
NOAA 3 [-]
1 06920U 73086A   19274.89287296 -.00000047  00000-0 -15266-4 0  9992
2 06920 102.0634 243.0381 0006504 322.5367  92.1233 12.40341463 78103
NOAA 4 [-]
1 07529U 74089A   19274.91067365 -.00000042  00000-0  16360-4 0  9998
2 07529 101.7661 241.5310 0008603 201.8927 218.8417 12.53134531 52599
NOAA 5 [-]
1 09057U 76077A   19274.94126271 -.00000044  00000-0  28578-5 0  9997
2 09057 101.9451 243.6082 0009635 169.0111 257.9812 12.37747719951301
TIROS N [P]
1 11060U 78096A   19274.78984841  .00000011  00000-0  26918-4 0  9992
2 11060  98.7795 331.0817 0011688 106.1012 254.1450 14.18244565331326
NOAA 6 [P]
1 11416U 79057A   19274.87548919  .00000007  00000-0  18722-4 0  9996
2 11416  98.6447 268.8307 0009394 301.5694  58.4572 14.33545268 99730
NOAA 7 [-]
1 12553U 81059A   19274.90465863 -.00000045  00000-0  58210-6 0  9995
2 12553  99.0973 284.6864 0012218  48.0331  13.3733 14.17263702977620
NOAA 8 [-]
1 13923U 83022A   19274.87273514 -.00000003  00000-0  16053-4 0  9996
2 13923  98.5924 258.5620 0014303 224.4989 135.5045 14.28682148901102
NOAA 9 [P]
1 15427U 84123A   19274.86274637 -.00000008  00000-0  18644-4 0  9999
2 15427  98.9023 223.6801 0015867  94.9702 322.1571 14.16077286796557
NOAA 10 [-]
1 16969U 86073A   19274.89842395 -.00000018  00000-0  97716-5 0  9991
2 16969  98.4859 268.4539 0011837 342.4621  76.0136 14.28079392719594
NOAA 11 [-]
1 19531U 88089A   19274.71335508 -.00000029  00000-0  60831-5 0  9992
2 19531  98.4399 303.4328 0011826 147.4606 212.7300 14.15245492600820
NOAA 12 [-]
1 21263U 91032A   19274.89342443 -.00000022  00000-0  87061-5 0  9991
2 21263  98.5154 287.3204 0013620   0.1550 359.9632 14.25899345475707
NOAA 13 [-]
1 22739U 93050A   19274.91555929  .00000007  00000-0  25937-4 0  9995
2 22739  98.4682 292.0211 0008520 303.3627  56.6731 14.12737801347330
NOAA 14 [-]
1 23455U 94089A   19274.85779253 -.00000013  00000-0  15211-4 0  9997
2 23455  98.5855 332.0973 0008352 285.8434  74.1819 14.14134667276844
NOAA 15 [B]
1 25338U 98030A   19274.88131921  .00000009  00000-0  22369-4 0  9992
2 25338  98.7423 295.9342 0009438 300.3560  59.6686 14.25932944111984
NOAA 16 [-]
1 26536U 00055A   19274.86212045 -.00000000  00000-0  23004-4 0  9997
2 26536  98.7669 344.7264 0011612 104.6519 255.5941 14.13236228277577
NOAA 17 [-]
1 27453U 02032A   19274.86904174 -.00000009  00000-0  14651-4 0  9991
2 27453  98.5471 222.5170 0010540 275.6991  84.2986 14.25048228897912
NOAA 18 [B]
1 28654U 05018A   19274.83125389  .00000061  00000-0  58033-4 0  9991
2 28654  99.0850 323.3205 0013482 239.8087 120.1749 14.12455433740266
NOAA 19 [+]
1 33591U 09005A   19274.88964586 -.00000021  00000-0  14129-4 0  9997
2 33591  99.1876 268.5944 0014972  83.9576 276.3300 14.12378214548496
SUOMI NPP [+]
1 37849U 11061A   19274.87535106  .00000016  00000-0  28308-4 0  9990
2 37849  98.7064 211.6542 0000760  69.3724 335.3272 14.19552738410805
NOAA 20 [+]
1 43013U 17073A   19274.76028927 -.00000013  00000-0  14796-4 0  9999
2 43013  98.7263 211.3465 0001188  67.0897 293.0404 14.19544261 96818
"""

    def setUp(self):
        """
        Initialize the TLE Class
        :return:
        """
        self.cel = Celtrack()

    def test_freeze(self):
        """
        Check the time has been frozen
        :return:
        """
        assert datetime.now() == datetime(2019, 10, 2, 8, 15)

    @patch('tsat.Celtrack.get', return_value=weather)
    def test_get(self, mock_function):
        data = self.cel.get("weather_url")
        self.assertEqual(data, self.weather)
        return data

    def test_read_tle_data(self):
        sat_data_obj = self.cel.read_tle_data(self.weather)
        self.assertIsNotNone(sat_data_obj)
        self.assertIsInstance(sat_data_obj, Satellites, "Correct Datatype returned")
        self.assertEqual(len(sat_data_obj), 22, "Correct internal length")
        self.assertIsInstance(sat_data_obj.getsat(0), SatData)
        self.assertIsInstance(sat_data_obj.getname(0), str)
        self.assertEqual("NOAA 20 [+]", sat_data_obj.getname(0))
        self.assertEqual("NOAA 1 [-]", sat_data_obj.getname(21))

    def test_position(self):
        self.cel.read_tle_data(self.weather)
        noaa_19 = self.cel.satellites.find('NOAA 19 [+]')
        self.assertIsInstance(noaa_19, SatData)
        orbital_obj = twoline2rv(noaa_19.tle_line1, noaa_19.tle_line2, wgs72)
        # Date has been fixed by freeze - Just checking
        when = datetime.now()
        self.assertEqual(when, datetime(2019, 10, 2, 8, 15))
        position, velocity = orbital_obj.propagate(when.year, when.month, when.day, when.hour, when.minute, when.second)
        self.assertEqual(position,
                         (-507.5514798055022, 6146.9740680175055, 3758.9001047275615))
        self.assertEqual(velocity, (1.0706129975515926, 3.9175804410494726, -6.2248174225551685))

    def test_noradid(self):
        self.cel.read_tle_data(self.weather)
        noaa_19 = self.cel.satellites.find('NOAA 19 [+]')
        self.assertIsInstance(noaa_19, SatData)
        orbital_obj = twoline2rv(noaa_19.tle_line1, noaa_19.tle_line2, wgs72)
        self.assertEqual(33591, orbital_obj.satnum)

    def test_all_positions(self):
        self.cel.read_tle_data(self.weather)
        noaa_19_sd = self.cel.satellites.find('NOAA 19 [+]')
        self.assertIsInstance(noaa_19_sd, SatData)
        noaa19 = ephem.readtle(noaa_19_sd.name, noaa_19_sd.tle_line1, noaa_19_sd.tle_line2)
        noaa19.compute(datetime.now())

        location = SatPos('NOAA 19 [+]')
        self.assertIsInstance(location, SatPos)
        # Make some datetimes
        midnight = datetime.replace(datetime.now(), hour=0)
        dt = [midnight + timedelta(minutes=1 * x) for x in range(0, 3 * 24 * 60)]
        # Compute satellite locations at each datetime
        for date in dt:
            self.cel.location.date = date
            noaa19.compute(self.cel.location)
            sat_observed = SatLoc(when=date,
                                  el=np.rad2deg(noaa19.alt),
                                  az=np.rad2deg(noaa19.az))
            if sat_observed.az >= -90.0:
                # Should be everything
                location.positions.append(sat_observed)
        self.assertEqual(4320, len(location.positions))

    def test_above_min_az_positions(self):
        self.cel.read_tle_data(self.weather)
        noaa_19_sd = self.cel.satellites.find('NOAA 19 [+]')
        self.assertIsInstance(noaa_19_sd, SatData)
        noaa19 = ephem.readtle(noaa_19_sd.name, noaa_19_sd.tle_line1, noaa_19_sd.tle_line2)
        noaa19.compute(datetime.now())

        location = SatPos('NOAA 19 [+]')
        self.assertIsInstance(location, SatPos)
        # Make some datetimes
        starttime = datetime.now()
        endtime = starttime + timedelta(days=3)

        next = []
        while True:
            next_pass = self.cel.location.next_pass(noaa19, singlepass=False)
            next.append(next_pass)
            # Update the date
            self.cel.location.date = datetime(next_pass[4].tuple()[0],
                                              next_pass[4].tuple()[1],
                                              next_pass[4].tuple()[2],
                                              next_pass[4].tuple()[3],
                                              next_pass[4].tuple()[4],
                                              int(next_pass[4].tuple()[5])) \
                                     + timedelta(minutes=5)
            if self.cel.location.date > endtime:
                break
            junk = 1
        #     self.cel.location.date = date
        #     sat_observed = SatLoc(when=date,
        #            el=np.rad2deg(noaa19.alt),
        #            az=np.rad2deg(noaa19.az))
        #     if sat_observed.az>= self.cel.min_ele:
        #         #Should be everything
        #         location.positions.append(sat_observed)
        # self.assertEqual(4320, len(location.positions))
