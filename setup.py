from setuptools import setup, find_packages

# To use a consistent encoding
import re
from codecs import open
from os import path
import datetime

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open("radie/__init__.py", "r") as f:
    lines = f.readlines()
    version_line = [line for line in lines if line.startswith('__version__')][0]
    version = version_line.split('=')[1].strip().replace("'", "")

setup(
    name='radie',
    version=version,
    description='a python application to rapidly import and view experimental data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://www.github.com/dvincentwest/radie',

    # Author details
    author='D. Vincent West',
    author_email='dvincentwest@gmail.com',

    # Choose your license
    license='GPLv2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords='data visualization',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    python_requires='>=3.5',
    install_requires=[
        'numpy',
        'pandas',
    ],
    extras_require={},
    package_data={
        'radie.plugins.examples': ['data/*'],
        'radie.qt': ['resources/icons/*.svg'],
        'radie.plugins.visualizations': ['icons/*.svg'],
    },
    data_files=[],
    entry_points={},
)
