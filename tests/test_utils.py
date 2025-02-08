from unittest import TestCase
from ddt import ddt, data, unpack

from utils import Utils

@ddt
class TestUtils(TestCase):
    @data(
        [
            {
                "a": 1,
                "b": {
                    "c": 2,
                    "d": {
                        "e": 3,
                        "f": [],
                    }
                },
                "g": {
                    'c': 5,
                    'd': {
                        'e':6,
                        'z':{},
                    },
                },
            },
            ['/b/d/f', '/g/d/z']
        ],
    )
    @unpack
    def test_depth_first_scan(self, input, expect):
        res = Utils.depth_first_scan(input)
        assert res == expect