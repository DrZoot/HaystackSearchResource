from distutils.core import setup
from setuptools import find_packages

setup(
      name='HaystackResource',
      version='0.0.1',
      author='Paul Gower',
      author_email='gmail.com',
      packages=['haystackresource'],
      url='https://github.com/DrZoot/HaystackSearchResource',
      license='Unlicense license, see LICENSE.txt',
      description='Base class for haystack backed searching in tastypie models',
      zip_safe=False,
)