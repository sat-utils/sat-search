from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '0.1.0'

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
    name='ssearch',
    version=__version__,
    description='A python wrapper for sat-api',
    long_description=long_description,
    url='https://github.com/sat-utils/sat-search',
    license='CC0',
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
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Alireza J (scisco)',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='alireza@developmentseed.org',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
