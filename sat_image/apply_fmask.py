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

from sat_image.image import LandsatImage

from sat_image.fmask import Fmask


def fmask(directory):
    dirs = [os.path.join(directory, x) for x in os.listdir(directory)]
    for d in dirs:
        l = LandsatImage(d)
        f = Fmask(l)
        pass

if __name__ == '__main__':
    home = os.path.expanduser('~')
    top_level = os.path.join(home, 'images', 'irrigation',
                             'MT', 'landsat', 'LC8_39_27')
    fmask(top_level)

# ========================= EOF ====================================================================
