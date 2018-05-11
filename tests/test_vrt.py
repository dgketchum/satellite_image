# =============================================================================================
# Copyright 2018 dgketchum
#
# Licensed under the Apache License, Version 2. (the "License");
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
# =============================================================================================
import os
import unittest
import shutil

from rasterio import open as rasopen

from sat_image import warped_vrt


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.origin = os.path.join('data', 'vrt_test')
        self.satellite = 'LC8'
        self.directory = os.path.join('data', 'vrt_test_copy')
        shutil.copytree(self.origin, self.directory)

    def test_warped_vrt(self):
        warped_vrt.warp_vrt(self.directory)
        shapes = []
        dirs = [_ for _ in os.listdir(self.directory) if not _.endswith('.txt')]
        for d in dirs:
            lst = [_ for _ in os.listdir(os.path.join(self.directory, d)) if _.endswith('.TIF')]
            for l in lst:
                tif = os.path.join(self.directory, d, l)
                with rasopen(tif, 'r') as src:
                    shapes.append(src.shape)

        shutil.rmtree(self.directory)
        self.assertEqual(shapes[0], shapes[1])


if __name__ == '__main__':
    unittest.main()

# ========================= EOF ====================================================================
