# =============================================================================================
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
# =============================================================================================

import os
import rasterio
import numpy as np


class UnmatchedStackGeoError(ValueError):
    pass


class InvalidObjectError(TypeError):
    pass


class SatelliteImage:
    def __init__(self, obj):
        self.obj = obj
        self._valid_formats = ['.tif', ]
        if os.path.isdir(obj):
            self.isdir = True
            self.isfile = False
        elif os.path.isfile(obj):
            self.isfile = True
            self.isdir = False
        else:
            raise InvalidObjectError(TypeError(
                'Object appears to be neither file nor directory...'))

        if self.isdir:
            self.image_list = []
            file_list = os.listdir(obj)
            for item in file_list:
                for form in self._valid_formats:
                    if item.lower().endswith(form):
                        self.image_list.append(item)

        else:
            self.image_list = None


class SingleImage(SatelliteImage):
    def get_ndarray(self):
        with rasterio.open(self.obj, 'r+') as r:
            arr = r.read()
            return arr

    def get_geo_attrs(self):
        with rasterio.open(self.obj, 'r+') as r:
            profile = r.profile
            return profile


class StackImage(SatelliteImage):

    def __init__(self, obj):

        super().__init__(obj)

        first = True

        with rasterio.open(self.obj, 'r+') as r:
            profile = r.profile
            if first:
                self.geo = profile
                first = False
            elif profile['crs'] == self.geo['crs']:
                pass
            else:
                raise UnmatchedStackGeoError(ValueError)

    def get_numpy_stack(self):

        stack_list = []

        for image in self.image_list:
            with rasterio.open(os.path.join(self.obj, image), 'r+') as r:
                arr = r.read()
                stack_list.append(arr)

        stack = np.empty((len(stack_list), self.geo['width'], self.geo['height']))

        for i, arr in enumerate(stack_list):
            stack[i] = arr

        return stack

if __name__ == '__main__':
    pass

# =============================================================================================
