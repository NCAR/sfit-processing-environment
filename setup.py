""" setup script """
""" python3 setup.py sdist """

from distutils.core import setup

# third-party libraries needed
install_requires = ['os', 'sys', 'numpy', 'matplotlib', 'Tkinter', 'datetime', 'time', 'math', 'csv', 'itertools', 'collections', 're', 'scipy', 'pyhdf', 'cycler', 'h5py',
                    'abc', 'getopt', 'glob', 'logging', 'shutil', 'fileinput', 'subprocess', 'netCDF4'] 

setup(
    name='sfit4-ProcessingEnvironment',
    version='1.0dev',
    packages=['HDFread', 'HDFsave', 'Layer0', 'Layer1', 'ModLib', 'Plotting', 'RefProfiles', 'SpectralDatabase'],
    license='NCAR, Boulder CO, USA; See license.txt',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    author='Eric Nussbaumer, James Hannigan, Ivan Ortega',
    author_email='iortge@ucar.edu',
    url='https://wiki.ucar.edu/display/sfit4/Infrared+Working+Group+Retrieval+Code%2C+SFIT',
    python_requires='>=2.7',
)