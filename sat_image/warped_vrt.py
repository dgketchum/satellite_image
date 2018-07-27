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

from __future__ import division

import os
from datetime import datetime

from rasterio import open as rasopen
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from sat_image.band_map import BandMap
from sat_image.image import Landsat5, Landsat7, Landsat8, LandsatImage


def warp_vrt(directory, delete_extra=False, use_band_map=False, overwrite=False):
    """ Read in image geometry, resample subsequent images to same grid.

    The purpose of this function is to snap many Landsat images to one geometry. Use Landsat578
    to download and unzip them, then run them through this to get identical geometries for analysis.
    Files
    :param use_band_map:
    :param delete_extra:
    :param directory: A directory containing sub-directories of Landsat images.
    :return: None
    """
    if 'resample_meta.txt' in os.listdir(directory) and not overwrite:
        print('{} has already had component images warped'.format(directory))
        return None

    mapping = {'LC8': Landsat8, 'LE7': Landsat7, 'LT5': Landsat5}

    vrt_options = {}
    list_dir = [x[0] for x in os.walk(directory) if os.path.basename(x[0])[:3] in mapping.keys()]

    first = True

    for d in list_dir:
        sat = LandsatImage(d).satellite
        paths = []
        root = os.path.join(directory, d)
        if os.path.isdir(root):
            for x in os.listdir(root):
                if use_band_map:
                    bands = BandMap().selected
                    for y in bands[sat]:
                        if x.endswith('B{}.TIF'.format(y)):
                            paths.append(os.path.join(directory, d, x))
                else:
                    if x.endswith('.TIF'):
                        paths.append(os.path.join(directory, d, x))
                if x.endswith('MTL.txt'):
                    mtl = os.path.join(directory, d, x)

        if first:

            landsat = mapping[sat](os.path.join(directory, d))
            dst = landsat.rasterio_geometry

            vrt_options = {'resampling': Resampling.cubic,
                           'dst_crs': dst['crs'],
                           'dst_transform': dst['transform'],
                           'dst_height': dst['height'],
                           'dst_width': dst['width']}


            message = """
            This directory has been resampled to same grid.
            Master grid is {}.
            {}
            """.format(d, datetime.now())
            with open(os.path.join(directory, 'resample_meta.txt'), 'w') as f:
                f.write(message)
            first = False

        os.rename(mtl, mtl.replace('.txt', 'copy.txt'))

        for tif_path in paths:
            print('warping {}'.format(os.path.basename(tif_path)))
            with rasopen(tif_path, 'r') as src:
                with WarpedVRT(src, **vrt_options) as vrt:
                    data = vrt.read()
                    dst_dir, name = os.path.split(tif_path)
                    outfile = os.path.join(dst_dir, name)
                    meta = vrt.meta.copy()
                    meta['driver'] = 'GTiff'
                    with rasopen(outfile, 'w', **meta) as dst:
                        dst.write(data)

        os.rename(mtl.replace('.txt', 'copy.txt'), mtl)

        if delete_extra:
            for x in os.listdir(os.path.join(directory, d)):
                x_file = os.path.join(directory, d, x)
                if x_file not in paths:
                    if x[-7:] not in ['ask.tif', 'MTL.txt']:
                        print('removing {}'.format(x_file))
                        os.remove(x_file)


if __name__ == '__main__':
    home = os.path.expanduser('~')
    images = os.path.join(home, 'landsat_images', 'vrt_testing')
    warp_vrt(images, delete_extra=True, use_band_map=True)

# ========================= EOF ================================================================
