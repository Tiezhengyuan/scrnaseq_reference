from unittest import TestCase
from ddt import ddt, data, unpack

from slicer import Slicer

@ddt
class TestSlicer(TestCase):
    @data(
        ['SRR10100029', ['SRR101', '029', 'SRR10100029']],
        ['SRR2760040', ['SRR276, '000', 'SRR2760040']],
        ['SRR27602699', ['SRR276', '099', 'SRR27602699']],
    )
    @unpack
    def test_SRR(self, input, expect):
        res = Slicer.SRR(input)
        assert res == expect