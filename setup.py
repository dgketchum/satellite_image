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

os.environ['TRAVIS_CI'] = 'True'

try:
    from setuptools import setup

    # setup_kwargs = {'entry_points': {'console_scripts': ['sat_image=sat_image.landsat_cli:cli_runner']}}
except ImportError:

    from distutils.core import setup

    # setup_kwargs = {'scripts': ['bin/sat_image/landsat_cli']}

with open('README.md') as f:
    readme = f.read()

tag = '0.1.22'
name = 'SatelliteImage'

setup(name=name,
      version=tag,
      description='Simple API provides a class to process satellite images',
      setup_requires=['nose>=1.0'],
      license='Apache',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: GIS',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6'],
      keywords='landsat download hydrology remote sensing',
      author='David Ketchum',
      author_email='dgketchum@gmail.com',
      platforms='Posix; MacOS X; Windows',
      packages=['sat_image'],
      download_url='https://github.com/{}/{}/archive/{}.tar.gz'.format('dgketchum', 'Landsat578', tag),
      url='https://github.com/dgketchum',
      test_suite='tests.test_suite.suite',
      install_requires=['numpy', 'rasterio==1.0a12', 'shapely', 'fiona', 'pyproj', 'scipy'])
# **setup_kwargs)

# ============= EOF ===========================================================================
