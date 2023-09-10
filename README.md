
# pyitt

pyitt is a Python binding to Intel Instrumentation and Tracing Technology (ITT) API. It provides a convenient way
to mark up the Python code for further performance analysis using performance analyzers from Intel like Intel VTune
or others.

pyitt supports following ITT APIs:
 - Collection Control API
 - Domain API
 - String Handle API
 - Id API *(partial support)*
 - Task API *(partial support)*

## Usage

The main goal of the project is to provide the ability to instrument a Python code using ITT API in the Pythonic way.
pyitt provides wrappers that simplify markup of Python code.

```python
import pyitt

@pyitt.task
def workload():
  pass

workload()
```

`pyitt.task` can be used as a decorator. In this case, the name of a callable object (`workload` function in this
example) will be used as a name of the task and the task will be attributed to a default domain named 'pyitt'.
If you want to change the default name and/or other parameters for the task (e.g. task domain), you can pass
them as arguments to `pyitt.task`:

```python
import pyitt

@pyitt.task('My Task', domain='My Task Domain')
def workload():
  pass

workload()
```

Also, `pyitt.task` returns the object that can be used as a context manager:

```python
import pyitt

with pyitt.task():
    # some code here...
    pass
```

If the task name is not specified, the `pyitt.task` uses call site information (filename and line number) to give
the name to the task. A custom name for the task and other task parameters can be specified via arguments
for `pyitt.task` in the same way as for the decorator form.

## Build

The native part of pyitt module is written using C++20 standard, therefore you need a compiler that supports this
standard, for example GCC-13 for Linux and Visual Studio 2022 for Windows.

### Ubuntu 22.04

 1. Install the compiler and Python utilities to build module:

        sudo add-apt-repository ppa:ubuntu-toolchain-r/test
        sudo apt update
        sudo apt install gcc-13 g++-13 python3-pip

 2. Get ITT headers and static library:
    *Option 1:* Download and install [Intel VTune for Linux](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler-download.html?operatingsystem=linux).
    *Option 2:* Build Intel ITT from [source](https://github.com/intel/ittapi).

 3. Clone the repository:

        git clone https://github.com/esuldin/pyitt.git

 4. Prepare the build environment: specify the compiler and the path to ITT header and static library.

        export CC=`which gcc-13`
        export CXX=`which g++-13`
        export VTUNE_PROFILER_DIR=/opt/intel/oneapi/vtune/latest

 5. Build and install pyitt:

        cd pyitt
        pip install .

### Windows 10/11

 1. Install [Python 3.8+](https://www.python.org/downloads/) together with pip utility.

 2. Install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/).
     Make sure that "Desktop development with C++" workload is selected.

 4. Get ITT headers and static library:
    *Option 1:* Download and install [Intel VTune for Windows](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler-download.html?operatingsystem=window).
    *Option 2:* Build Intel ITT from [source](https://github.com/intel/ittapi).

 5. Clone the repository

        git clone https://github.com/esuldin/pyitt.git

5. Prepare the build environment: specify the paths to Python and to ITT header and static library.

        set PATH=C:\Program Files\Python38;C:\Program Files\Python38\Scripts;%PATH%
        set VTUNE_PROFILER_DIR=C:\Program Files (x86)\Intel\oneAPI\vtune\latest

6. Build and install pyitt

        cd pyitt
        pip install .

## References

 - [Instrumentation and Tracing Technology APIs](https://www.intel.com/content/www/us/en/docs/vtune-profiler/user-guide/2023-0/instrumentation-and-tracing-technology-apis.html)
 - [Intel® VTune™ Profiler User Guide - Task Analysis](https://www.intel.com/content/www/us/en/docs/vtune-profiler/user-guide/2023-0/task-analysis.html)
