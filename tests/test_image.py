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
import numpy as np
import rasterio
from rasterio.transform import Affine
from datetime import date

from sat_image.image import LandsatImage, Landsat5, Landsat7, Landsat8


class LandsatImageTestCase(unittest.TestCase):
    def setUp(self):
        self.dir_name_LT5 = 'data/image_test/lt5_image'

    def test_earth_sun(self):
        landsat = LandsatImage(self.dir_name_LT5)
        dist_au = landsat.earth_sun_dist
        self.assertAlmostEqual(dist_au, 1.01387, delta=0.01)

    def test_mask_poly(self):
        landsat = LandsatImage(self.dir_name_LT5)
        shape = landsat.get_tile_geometry()
        self.assertEqual(shape[0]['coordinates'][0],
                         [(367035.0, 5082585.0),
                          (388845.0, 5082585.0), (388845.0, 5060775.0),
                          (367035.0, 5060775.0), (367035.0, 5082585.0)])

    def test_date(self):
        landsat = LandsatImage(self.dir_name_LT5)
        self.assertEqual(date(2006, 7, 6), landsat.date_acquired)


class Landsat5TestCase(unittest.TestCase):
    def setUp(self):
        self.dir_name_LT5 = 'data/image_test/lt5_image'
        # results from fmask.exe
        # bitbucket.org/chchrsc/python-fmask/
        self.exp_reflect = 'data/image_test/lt5_image/LT5_reflct_10000x_b1.tif'
        self.l5 = Landsat5(self.dir_name_LT5)
        self.cell = 150, 150

    def test_instantiate_scene(self):
        self.assertTrue(self.l5.isdir)
        self.assertEqual(self.l5.mtl['L1_METADATA_FILE']['PRODUCT_METADATA']['FILE_NAME_BAND_1'],
                         'LT05_L1TP_040028_20060706_20160909_01_T1_B1.TIF')
        self.assertEqual((self.l5.profile['height'], self.l5.profile['width']),
                          (727, 727))
        self.assertEqual(self.l5.utm_zone, 12)
        self.assertEqual(self.l5.ex_atm_irrad, (1958.0, 1827.0, 1551.0,
                                                1036.0, 214.9, np.nan, 80.65))

        self.assertEqual(self.l5.rasterio_geometry['height'], 727)
        self.assertEqual(self.l5.rasterio_geometry['driver'], 'GTiff')
        self.assertEqual(self.l5.rasterio_geometry['dtype'], 'uint16')
        self.assertEqual(self.l5.rasterio_geometry['transform'], (367035.0, 30.0, 0.0, 5082585.0, 0.0, -30.0))

    def test_reflectance(self):
        toa_reflect = self.l5.reflectance(1)[self.cell]
        qcal = self.l5._get_band('b1')[self.cell]
        qcal_min = self.l5.quantize_cal_min_band_1
        qcal_max = self.l5.quantize_cal_max_band_1
        l_min = self.l5.radiance_minimum_band_1
        l_max = self.l5.radiance_maximum_band_1
        radiance = ((l_max - l_min) / (qcal_max - qcal_min)) * (qcal - qcal_min) + l_min
        toa_reflect_test = (np.pi * radiance) / ((1 / (self.l5.earth_sun_dist ** 2)) * self.l5.ex_atm_irrad[0] * np.cos(
            self.l5.solar_zenith_rad))
        self.assertAlmostEqual(toa_reflect_test, toa_reflect, delta=0.001)
        self.assertAlmostEqual(toa_reflect, 0.1105287, delta=0.001)

        with rasterio.open(self.exp_reflect, 'r') as src:
            reflct = src.read(1)
            reflct = np.array(reflct, dtype=np.float32)
            reflct[reflct == 32767.] = np.nan
            reflct *= 1 / 10000.

        self.assertAlmostEqual(reflct[self.cell], toa_reflect, delta=0.01)

    def test_brightness(self):
        bright = self.l5.brightness_temp(6)
        self.assertAlmostEqual(bright[self.cell], 298.55, delta=0.01)

    def test_albedo(self):
        albedo = self.l5.albedo()[self.cell]
        # inputs for self.cell toa reflect b 1, 3, 4, 5, 7
        l = [0.11047232299890863, 0.094736151248181175, 0.22708428311416637, 0.23499215186750311, 0.13805073521100206]
        exp_alb = (0.356 * l[0] + 0.130 * l[1] + 0.373 * l[2] + 0.085 * l[3] + 0.072 * l[4] - 0.0018) / 1.014
        self.assertAlmostEqual(exp_alb, albedo, delta=0.001)

    def test_saturation_mask(self):
        green_mask = self.l5.saturation_mask(2)
        red_mask = self.l5.saturation_mask(3)
        green_sat_cell = 175, 381
        red_sat_cell = 96, 305
        self.assertTrue(green_mask[green_sat_cell])
        self.assertTrue(red_mask[red_sat_cell])

    def test_ndsi(self):
        ndvi = self.l5.ndvi()[self.cell]
        b4, b3 = self.l5.reflectance(4)[self.cell], self.l5.reflectance(3)[self.cell]
        ndvi_exp = (b4 - b3) / (b4 + b3)
        self.assertEqual(ndvi, ndvi_exp)

    def test_ndsi(self):
        ndsi = self.l5.ndsi()[self.cell]
        b2, b5 = self.l5.reflectance(2)[self.cell], self.l5.reflectance(5)[self.cell]
        ndsi_exp = (b2 - b5) / (b2 + b5)
        self.assertEqual(ndsi, ndsi_exp)


class Landsat7TestCase(unittest.TestCase):
    def setUp(self):
        # results from fmask.exe
        # bitbucket.org/chchrsc/python-fmask/
        self.dir_name_LT7 = 'data/image_test/le7_image'
        self.exp_reflect = 'data/image_test/le7_image/LE7_reflct_10000x_b1.tif'
        self.l7 = Landsat7(self.dir_name_LT7)
        self.cell = 300, 300

    def test_instantiate_scene(self):
        self.assertEqual(self.l7.mtl['L1_METADATA_FILE']['PRODUCT_METADATA']['FILE_NAME_BAND_1'],
                         'LE07_L1TP_039028_20100702_20160915_01_T1_B1.TIF')
        self.assertEqual(self.l7.utm_zone, 12)
        self.assertEqual(self.l7.ex_atm_irrad, (1970.0, 1842.0, 1547.0, 1044.0,
                                                255.700, np.nan, 82.06, 1369.00))
        self.assertEqual(self.l7.rasterio_geometry['height'], 727)
        self.assertEqual(self.l7.rasterio_geometry['driver'], 'GTiff')
        self.assertEqual(self.l7.rasterio_geometry['dtype'], 'uint8')
        self.assertEqual(self.l7.rasterio_geometry['transform'], (367035.0, 30.0, 0.0, 5082585.0, 0.0, -30.0))

    def test_reflectance(self):
        toa_reflect = self.l7.reflectance(1)

        with rasterio.open(self.exp_reflect, 'r') as src:
            reflct = src.read(1)
            reflct = np.array(reflct, dtype=np.float32)
            reflct[reflct == 32767.] = np.nan
            reflct *= 1 / 10000.

        toa_reflect = np.where(np.isnan(reflct), reflct, toa_reflect)

        self.assertAlmostEqual(reflct[self.cell], toa_reflect[self.cell], delta=0.01)

    def test_brightness(self):
        bright = self.l7.brightness_temp(6)
        self.assertAlmostEqual(bright[self.cell], 259.98, delta=0.01)

    def test_albedo(self):
        albedo = self.l7.albedo()[self.cell]
        # inputs for self.cell toa reflect b 1, 3, 4, 5, 7
        l = [0.30141704688299908, 0.26113788900694823, 0.37401738034983784, 0.15728264090788563, 0.11929144012910768]
        exp_alb = (0.356 * l[0] + 0.130 * l[1] + 0.373 * l[2] + 0.085 * l[3] + 0.072 * l[4] - 0.0018) / 1.014
        self.assertAlmostEqual(exp_alb, albedo, delta=0.001)

    def test_saturation_mask(self):
        green_mask = self.l7.saturation_mask(2)
        red_mask = self.l7.saturation_mask(3)
        green_sat_cell = 65, 398
        red_sat_cell = 4, 52
        self.assertTrue(green_mask[green_sat_cell])
        self.assertTrue(red_mask[red_sat_cell])

    def test_ndvi(self):
        ndvi = self.l7.ndvi()
        ndvi_cell = ndvi[self.cell]
        b4, b3 = self.l7.reflectance(4)[self.cell], self.l7.reflectance(3)[self.cell]
        ndvi_exp = (b4 - b3) / (b4 + b3)
        self.assertEqual(ndvi_cell, ndvi_exp)
        home = os.path.expanduser('~')
        outdir = os.path.join(home, 'images', 'sandbox')
        self.l7.save_array(ndvi, os.path.join(outdir, 'ndvi.tif'))

    def test_ndsi(self):
        ndsi = self.l7.ndsi()[self.cell]
        b2, b5 = self.l7.reflectance(2)[self.cell], self.l7.reflectance(5)[self.cell]
        ndsi_exp = (b2 - b5) / (b2 + b5)
        self.assertEqual(ndsi, ndsi_exp)


class Landsat8TestCase(unittest.TestCase):
    def setUp(self):
        self.dirname_cloud = 'data/image_test/lc8_image'
        # results from rio-toa
        self.ex_bright = os.path.join(self.dirname_cloud, 'LC8_brightemp_B10.TIF')
        self.ex_reflect = os.path.join(self.dirname_cloud, 'LC8_reflct_B1.TIF')
        self.cell = 300, 300

    def test_instantiate_scene(self):
        l8 = Landsat8(self.dirname_cloud)
        self.assertEqual(l8.mtl['L1_METADATA_FILE']['PRODUCT_METADATA']['FILE_NAME_BAND_1'],
                         'LC80400282014193LGN00_B1.TIF')
        self.assertEqual(l8.utm_zone, 12)

        self.assertEqual(l8.rasterio_geometry['height'], 727)
        self.assertEqual(l8.rasterio_geometry['driver'], 'GTiff')
        self.assertEqual(l8.rasterio_geometry['dtype'], 'uint16')
        self.assertEqual(l8.rasterio_geometry['transform'], (367035.0, 30.0, 0.0, 5082585.0, 0.0, -30.0))

    def test_toa_brightness(self):
        l8 = Landsat8(self.dirname_cloud)

        with rasterio.open(self.ex_bright, 'r') as src:
            ex_br = src.read(1)
        bright = l8.brightness_temp(10)
        self.assertEqual(bright.shape, ex_br.shape)
        self.assertAlmostEqual(ex_br[self.cell],
                               bright[self.cell],
                               delta=0.001)

    def test_toa_reflectance(self):
        l8 = Landsat8(self.dirname_cloud)
        with rasterio.open(self.ex_reflect, 'r') as src:
            expected_reflectance = src.read(1)
        reflectance = l8.reflectance(1)

        # toa has a problem
        #
        # self.assertAlmostEqual(expected_reflectance[self.cell],
        #                        reflectance[self.cell],
        #                        delta=0.001)

    def test_albedo(self):
        l8 = Landsat8(self.dirname_cloud)
        albedo = l8.albedo()[self.cell]
        # inputs for self.cell toa reflect b 2, 4, 5, 6, 7
        l = [0.021763351, 0.065929502, 0.33231941, 0.2018306, 0.10294776]
        exp_alb = (0.356 * l[0] + 0.130 * l[1] + 0.373 * l[2] + 0.085 * l[3] + 0.072 * l[4] - 0.0018) / 1.014
        self.assertAlmostEqual(exp_alb, albedo, delta=0.001)

    def test_ndvi(self):
        l8 = Landsat8(self.dirname_cloud)
        ndvi = l8.ndvi()[self.cell]
        b5, b4 = l8.reflectance(5)[self.cell], l8.reflectance(4)[self.cell]
        ndvi_exp = (b5 - b4) / (b5 + b4)
        self.assertEqual(ndvi, ndvi_exp)

    def test_ndsi(self):
        l8 = Landsat8(self.dirname_cloud)
        ndsi = l8.ndsi()[self.cell]
        b3, b6 = l8.reflectance(3)[self.cell], l8.reflectance(6)[self.cell]
        ndsi_exp = (b3 - b6) / (b3 + b6)
        self.assertEqual(ndsi, ndsi_exp)


if __name__ == '__main__':
    unittest.main()


# ===============================================================================
