from unittest import TestCase
from tsat import Satellites, SatData
from tests import test_celtrack


class TestSatellites(TestCase):

    def setUp(self):

        self.test_obj = Satellites()
        self.test_obj.append(SatData(name='ISS',tle_line1='line1',tle_line2='line2'))
        self.test_obj.append(SatData(name='Mariner', tle_line1='line1', tle_line2='line2'))
        self.test_obj.append(SatData(name='Voyager', tle_line1='line1', tle_line2='line2'))
        self.test_obj.append(SatData(name='Sputnik', tle_line1='line1', tle_line2='line2'))

    def test_find(self):
        for wanted in ['Sputnik','Mariner']:
            self.assertIsInstance(self.test_obj.find(wanted),SatData)

    def test_notfound(self):
        for wanted in ['Apollo']:
            self.assertIsNone(self.test_obj.find(wanted),None)


