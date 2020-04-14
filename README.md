# sfit4 - pre/post processing python package distribution

Python package used for pre and post-processing of sfit4 (sfit-processing-environment)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.
The step-by-step procedures and computing tools are described in OT-FTS_Spectral_Processing.pdf 

### Prerequisites

Below are the standard python libraries needed in order to run sfit-processing-environment.
The package has been tested with python >=2.7 
Note: The installation of these libraries are not covered here.  

```
os, sys, numpy, matplotlib, Tkinter, datetime, time, math, csv, itertools, collections, re, 
scipy, pyhdf, cycler, h5py, abc, getopt, glob, logging, shutil, fileinput, subprocess, netCDF4 
```

### Installing sfit-processing-environment

The sfit-processing-environment can be found here:

* [1) sfit4wiki](https://wiki.ucar.edu/display/sfit4/) - The NCAR sfit wiki webpage. Here you can download a tar file.

Installation via its setup.py script

Use tar to unpack the archive, for example: 

```
$ tar -xzf sfit4-ProcessingEnvironment-1.0dev.tar.gz
```

Change to the new directory (cd), and then, to install it in a prefered directory, for example, using python 3 enter

```
$ python3 setup.py install --home=<dir>
```

The --home option defines the installation base directory. Files are installed to the following directories under the installation base as follows: /dir/lib/python.
More information on [Installing Python Modules](https://docs.python.org/3.3/install/index.html/)

Alternatively, you can use --user option directs setup.py to install the package in the user site-packages directory for the running Python; for example:

```
python3 setup.py install --user
```
and will be installed, for example,

```
~//usr/local/lib/pythonX.Y/site-packages/
```

* [2) github](https://github.com/NCAR/sfit-processing-environment.git) - The NCAR github sfit - sfit-processing-environment.

This is the repository with several contributors. The branch with the relese version is release_v1.0.
To install release_v1.0 locally in the current working directory:

```
git clone -b release_v1.0 https://github.com/NCAR/sfit-processing-environment.git
```

### Deployment 

In theory, when using python3 setup.py install --user python automatically searches this directory for modules, so prepending this path to the PYTHONPATH environmental variable is not necessary. 
However, it is still recommended to add this directory to your PYTHONPATH and PATH environment variables. For example, add the following path to you
.bashrc (or .bash_profile), e.g., open your .bash_profile

```
$ vi ~/.bash_profile
```
and insert the following, for example,

```
export PATH=$PATH:/usr/local/lib/pythonX.Y/site-packages/Layer1
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/pythonX.Y/site-packages/Layer1
```

use the above for all folders.

Additionally, the main python scripts on each folder use the shebang:

```
#!/usr/bin/python3
```

you can either modify thie line with you prefered python version or over run by using, for example,

```
$ /usr/bin/python2.7 sfit4Layer1.py -?
```

## Running the tests

If the above packages have been added to the PATH & PYTHONPATH you can test

```
$ sfit4Layer1.py -?
```

otherwise go to, e.g., the Layer1 folder and type

```
$ python3 sfit4Layer1.py -?
```

## Versioning

**Version 1.0dev**. release version 1.0 (development)

## Authors

* **Eric Nusbaumer** - *Initial work* - 
* **Bavo Langerock** - *Current work* - 
* **Mathias Palm** - *Current work* - 
* **James Hannigan** - *Current work* - 
* **Ivan Ortega** - *Current work* - [iortegam](https://github.com/iortegam)


## Contributing


## License

See the [license.txt](license.txt) file for details

## Acknowledgments

* Garth DAttilo (NCAR, Boulder CO, 80301)

