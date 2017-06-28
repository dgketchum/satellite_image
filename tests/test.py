# ===============================================================================
# Copyright 2017 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

import unittest
import numpy as np
from pkg_resources import resource_filename

from image.image import SatelliteImage, StackImage, SingleImage


class ImageTestCase(unittest.TestCase):
    def setUp(self):
        self.invalid_string = 'blah'
        self.valid_file = False
        self.valid_dir = False
        self.dir_name = 'tests/data'
        self.image_list = ['LT50360292007146PAC01_B1.TIF', 'LT50360292007146PAC01_B2.TIF',
                           'LT50360292007146PAC01_B3.TIF', 'LT50360292007146PAC01_B4.TIF',
                           'LT50360292007146PAC01_B5.TIF', 'LT50360292007146PAC01_B6.TIF',
                           'LT50360292007146PAC01_B7.TIF']
        self.passed_file = resource_filename('tests', 'data/LT50360292007146PAC01_B1.TIF')

    def tearDown(self):
        pass

    def test_instantiate_file(self):
        s = SatelliteImage(self.passed_file)
        self.assertIsInstance(s, SatelliteImage)
        self.assertIsNone(s.image_list)

    def test_single_instance(self):
        s = SingleImage(self.passed_file)
        self.assertFalse(s.isdir)
        self.assertIsInstance(s, SingleImage)
        self.assertIsNone(s.image_list)

    def test_single_ndarray(self):
        s = SingleImage(self.passed_file)
        self.assertIsInstance(s.get_ndarray(), np.ndarray)

    def test_single_getgeo(self):
        s = SingleImage(self.passed_file)
        geo = s.geo
        self.assertIsInstance(geo, dict)
        self.assertEqual(geo['width'], 300)

    def test_instantiate_dir(self):
        s = SatelliteImage(self.dir_name)
        self.assertIsInstance(s, SatelliteImage)
        self.assertTrue(s.isdir)
        self.assertFalse(s.isfile)
        self.assertEqual(len(s.image_list), len(self.image_list))

    def test_stack_instance(self):
        s = StackImage(self.dir_name)
        self.assertFalse(s.isfile)
        self.assertIsInstance(s, StackImage)

    def test_numpy_stack(self):
        s = StackImage(self.dir_name)
        np_stack = s.get_numpy_stack()
        self.assertIsInstance(np_stack, np.ndarray)
        self.assertEqual(np_stack.ndim, 3)
        self.assertEqual(np_stack.shape, (7, 300, 300))


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
