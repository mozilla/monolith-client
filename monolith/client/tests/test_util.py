import unittest
import datetime

from monolith.client.util import (iterdays, itermonths, iteryears, iterweeks,
                                  num_months, num_weeks)


class TestIterators(unittest.TestCase):

    def setUp(self):
        self.start = datetime.date(2011, 01, 01)
        self.end = datetime.date(2012, 05, 01)

    def test_iterdays(self):
        # 487 days : 365 in 2011 + 4 months in 2012
        res = list(iterdays(self.start, self.end))
        self.assertEquals(len(res), 487)

    def test_iteryears(self):
        # 2 years
        res = list(iteryears(self.start, self.end))
        self.assertEquals(len(res), 2)

    def test_numweeks(self):
        self.assertEquals(num_weeks(self.start, self.end), 70)

    def test_iterweeks(self):
        # 52 weeks in 2011 + 18 weeks in 2012
        res = list(iterweeks(self.start, self.end))
        self.assertEquals(len(res), 70)

    def test_nummonths(self):
        self.assertEquals(num_months(self.start, self.end), 17)

    def test_itermonths(self):
        # 12 months in 2011, 6 months in 2012
        res = list(itermonths(self.start, self.end))
        self.assertEquals(len(res), 17)
