from setuptools import setup, find_packages
from imp import load_source
from os import path

__version__ = load_source('satsearch.version', 'satsearch/version.py').__version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

setup(
    name='satsearch',
    author='Matthew Hanson (matthewhanson)',
    version=__version__,
    description='A python client for sat-api',
    long_description=long_description,
    url='https://github.com/sat-utils/sat-search',
    license='MIT',
    classifiers=[
        'Framework :: Pytest',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Freeware',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='',
    entry_points={
        'console_scripts': ['sat-search=satsearch.main:cli'],
    },
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
