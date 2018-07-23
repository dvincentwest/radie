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

d = datetime.date.today()
version = "{:04d}.{:02d}.{:02d}".format(d.year, d.month, d.day)
with open("radie/__init__.py", "r") as f:
    text = f.read()
with open("radie/__init__.py", "w") as f:
    f.write(re.sub(".*__version__.*", '__version__ = "{:s}"'.format(version), text))

setup(
    name='radie',
    version=version,
    description='a python application to rapidly import and view experimental data',
    long_description=long_description,
    url='https://www.github.com/dvincentwest/radie',

    # Author details
    author='D. Vincent West',
    author_email='dvincentwest@gmail.com',

    # Choose your license
    license='GPLv2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Jupyter',
        'Environment :: Desktop'
        'Intended Audience :: Scientists',
        'License :: OSI Approved :: GNU General Public License version 2',
        'Programming Language :: Python',
        'Topic :: Scientific Data :: Visualization and Analysis',
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
