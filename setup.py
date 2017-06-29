# try:
#     from setuptools import setup
# except ImportError:
#     from distutils.core import setup

from setuptools import setup, find_packages

setup(
    name='mealtime',
    version='0.1.0b5',
    author='Sam Wu',
    author_email='samsam2310@gmail.com',
    packages=find_packages(),
    install_requires=['pymongo',
                      'tornado',
                      'requests'],
)
