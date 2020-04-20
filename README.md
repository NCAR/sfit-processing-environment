# sfit4 - pre/post processing python package distribution

Python package used for pre and post-processing of sfit4 (sfit-processing-environment)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.
The step-by-step procedures and computing tools are described in more detailed in the **OT_FTS_Spectral_Processing.pdf**

### Prerequisites

Below are the standard python libraries needed in order to run sfit-processing-environment.
The package has been tested with python >=2.7. However, Python 2.7 reached the end of its life on January 1st, 2020 and it is not maintaned.
Python3 is prefered.
Note: The installation of python3 and these libraries are not covered here.

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
More information on [Installing Python Modules](https://docs.python.org/3.3/install/index.html)

Alternatively, you can use --user option directs setup.py to install the package in the user site-packages directory for the running Python; for example:

```
python3 setup.py install --user
```
and will be installed, for example,

```
~//usr/local/lib/pythonX.Y/site-packages/
```

where X.Y stands for the version of Python, for example 3.8


* [2) github](https://github.com/NCAR/sfit-processing-environment.git) - The NCAR github sfit - sfit-processing-environment.

This is the repository with several contributors/branches. The branch with the relese version is **Official_Release_v3.0**.
To install Official_Release_v3.0 locally in the current working directory:

```
git clone -b Official_Release_v3.0 https://github.com/NCAR/sfit-processing-environment.git
```

### Deployment

In theory, when using python3 setup.py install --user python automatically searches this directory for modules, so prepending this path to the PYTHONPATH environmental variable is not necessary.
However, it is still recommended to add this directory to your PYTHONPATH and PATH environment variables. For example, add the following path to your shell, i.e., a program designed to start other programs (.bashrc, .bash_profile, .profile) e.g., open your .bash_profile

```
$ vi ~/.bash_profile
```
and insert the following, for example,

```
export PATH=$PATH:/usr/local/lib/pythonX.Y/site-packages/Layer1
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/pythonX.Y/site-packages/Layer1
```

<!-- V3.0 test -->
<!--SPE=/myhomedir/V3.0/lib/python -->
<!--export PYTHONPATH=$SPE/HDFread:$SPE/HDFsave:$SPE/Layer0:$SPE/Layer1:$SPE/ModLib:$SPE/Plotting:$SPE/RefProfiles:$SPE/SpectralDatabase:$PYTHONPATH -->


use the above for all folders.

Additionally, the main python scripts on each folder use the shebang (top line in any script for standalone executable without typing python):

```
#!/usr/bin/python3
```

you can either modify the line with your prefered python version or type your python version in the command line, for example,

```
$ /usr/bin/python2.7 sfit4Layer1.py -?
```

Depending on the installation, often, especially when using the --home option it is necessary to change permissions to the directory. In this case, you might use the command below under the directory, e.g., under /dir/lib/python

```
$ sudo chmod -R 755 *
```


## Running the tests

If the above packages have been added to the PATH & PYTHONPATH and the shebang has been modified to your python version you can test

```
$ sfit4Layer1.py -?
```

otherwise go to, e.g., the Layer1 folder and type

```
$ python3 sfit4Layer1.py -?
```

if succefully, the output might look like this

```
  -i <file>                              : Flag to specify input file for Layer 1 processing. <file> is full path and filename of input file
  -l                                     : Flag to create log files of processing. Path to write log files is specified in input file
  -L <0/1>                               : Flag to create output list file. Path to write list files is specified in input file
  -P <int>                               : Pause run starting at run number <int>. <int> is an integer to start processing at
  -d <20190101> or <20190101_20191231>   : Date or Date range
                                         -d is optional and if used these dates will overwrite dates in input file for Layer 1 processing
  -?                                     : Show all flags
```


## Versioning

**Version 3.0dev**. release version 3.0 (development)

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

