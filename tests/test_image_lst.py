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

import os
import unittest
from fiona import open as fopen
from rasterio import open as rasopen

from sat_image.image import Landsat8, Landsat5, Landsat7


class TestImageLST5(unittest.TestCase):
    def setUp(self):
        self.dir_name_LT5 = 'tests/data/ssebop_test/lt5/041_025/2000/LT50410252000194AAA01'
        self.l5 = Landsat5(self.dir_name_LT5)
        self.lst = self.l5.land_surface_temp()
        self.lst_raster_path = os.path.join(self.dir_name_LT5, 'lst5_test.tif')
        self.l5.save_array(self.lst, self.lst_raster_path)
        self.point_file = 'tests/data/points/041_025_CA_Let_points.shp'
        self.eef_lst_raster = os.path.join('tests/data/ssebop_test/lt5/041_025/2000/',
                                           'LT50410252000194AAA01',
                                           'LT50410252000194AAA01_LST_EEF.tif')

    def test_surface_temps(self):
        points_dict = raster_point_extract(lst_raster=self.lst_raster_path,
                                           eef_raster=self.eef_lst_raster,
                                           points=self.point_file)
        for key, val in points_dict.items():
            eef = val['eef_lst']
            lst = val['lst_found']
            ratio = eef / lst
            print('Ratio at {} of EEFlux:LST calculated is {}.'.format(
                key, ratio))
            self.assertAlmostEqual(ratio, 1.0, delta=0.01)
        os.remove(self.lst_raster_path)


class TestImageLST7(unittest.TestCase):
    def setUp(self):
        self.dir_name_LT7 = 'tests/data/ssebop_test/le7/041_025/2000/LE70410252000234PAC00'
        self.l7 = Landsat7(self.dir_name_LT7)
        self.lst = self.l7.land_surface_temp()
        self.lst_raster_path = os.path.join(self.dir_name_LT7, 'lst7_test.tif')
        self.l7.save_array(self.lst, self.lst_raster_path)
        self.point_file = 'tests/data/points/041_025_CA_Let_points.shp'
        self.eef_lst_raster = os.path.join('tests/data/ssebop_test/le7/041_025/2000',
                                           'LE70410252000234PAC00/LE70410252000234PAC00_LST_EEF.tif')

    def test_surface_temps(self):
        points_dict = raster_point_extract(lst_raster=self.lst_raster_path,
                                           eef_raster=self.eef_lst_raster,
                                           points=self.point_file)
        for key, val in points_dict.items():
            eef = val['eef_lst']
            lst = val['lst_found']
            ratio = eef / lst
            print('Ratio at {} of EEFlux:LST calculated is {}.'.format(
                key, ratio))
            self.assertAlmostEqual(ratio, 1.0, delta=0.01)
        os.remove(self.lst_raster_path)


class TestImageLST8(unittest.TestCase):
    def setUp(self):
        self.dir_name_LT8 = 'tests/data/ssebop_test/lc8/038_027/2014/LC80380272014227LGN01'
        self.l8 = Landsat8(self.dir_name_LT8)
        self.lst = self.l8.land_surface_temp()
        # self.lst_raster_path = os.path.join(self.dir_name_LT8, 'lst8_test.tif')
        self.lst_raster_path = '/data01/images/sandbox/lst8_test.tif'
        self.l8.save_array(self.lst, self.lst_raster_path)
        self.point_file = 'tests/data/points/038_027_US_Mj_points.shp'
        self.eef_lst_raster = os.path.join('tests/data/ssebop_test/lc8/038_027',
                                           '2014/LC80380272014227LGN01/LC80380272014227LGN01_LST_EEF.tif')

    def test_surface_temps(self):
        points_dict = raster_point_extract(lst_raster=self.lst_raster_path,
                                           eef_raster=self.eef_lst_raster,
                                           points=self.point_file)
        for key, val in points_dict.items():
            eef = val['eef_lst']
            lst = val['lst_found']
            ratio = eef / lst
            print('Ratio at {} of EEFlux:LST calculated is {}.'.format(
                key, ratio))
            self.assertAlmostEqual(ratio, 1.0, delta=0.01)
        os.remove(self.lst_raster_path)


# ===================== ANCILLARY FUNCTIONS =================================

def raster_point_extract(lst_raster, eef_raster, points):
    point_data = {}
    with fopen(points, 'r') as src:
        for feature in src:
            try:
                name = feature['properties']['Name']
            except KeyError:
                name = feature['properties']['FID']
            point_data[name] = {'coords': feature['geometry']['coordinates']}

        with rasopen(lst_raster, 'r') as src:
            lst_arr = src.read()
            lst_arr = lst_arr.reshape(lst_arr.shape[1], lst_arr.shape[2])
            lst_affine = src.transform

        with rasopen(eef_raster, 'r') as src:
            eef_lst = src.read()
            eef_lst = eef_lst.reshape(eef_lst.shape[1], eef_lst.shape[2])
            eef_affine = src.transform

        for key, val in point_data.items():
            x, y, z = val['coords']
            col, row = ~lst_affine * (x, y)
            val = lst_arr[int(row), int(col)]
            point_data[key]['lst_found'] = val
            point_data[key]['lst_row_col'] = int(row), int(col)

            col, row = ~eef_affine * (x, y)
            val = eef_lst[int(row), int(col)]
            point_data[key]['eef_lst'] = val
            point_data[key]['eef_row_col'] = int(row), int(col)

        return point_data


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
