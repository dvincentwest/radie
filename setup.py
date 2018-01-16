from setuptools import setup, find_packages

# To use a consistent encoding
import re
from codecs import open
from os import path
import datetime

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

d = datetime.date.today()
version = "{:04d}.{:02d}.{:02d}".format(d.year, d.month, d.day)
with open("dataquick/__init__.py", "r") as f:
    text = f.read()
with open("dataquick/__init__.py", "w") as f:
    f.write(re.sub(".*__version__.*", '__version__ = "{:s}"'.format(version), text))

setup(
    name='dataquick',
    version=version,
    description='',
    long_description=long_description,
    url='https://www.github.com/dvincentwest/dataquick',

    # Author details
    author='Vince West',
    author_email='dvincentwest@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Scientists',
        'Topic :: Scientific Data :: Visualization and Analysis',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='data visualization',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    python_requires='>=3.5',
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'pyqtgraph>=0.10',
        'PyQt5>=5.6',
    ],
    extras_require={},
    package_data={
        'dataquick.plugins.examples': ['data/*'],
        'dataquick.qt': ['resources/icons/*.svg'],
        'dataquick.plugins.visualizations': ['icons/*.svg'],
    },
    data_files=[],
    entry_points={},
)
