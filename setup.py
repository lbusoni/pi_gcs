# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pi_gcs',

    version='0.6',

    description='Unofficial python wrapper for Physik Instrumente General Command Set API',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/lbusoni/pi_gcs',

    # Author details
    author='Lorenzo Busoni',
    author_email='lbusoni@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='PI GCS2 GCS',

    #packages=find_packages(exclude=['test']),
    packages=['pi_gcs'],
    test_suite='test',
)
