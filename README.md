[![PyPI](https://badge.fury.io/py/pyitt.svg)](https://pypi.org/project/pyitt/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyitt)](https://pypi.org/project/pyitt/)
[![CI](https://github.com/esuldin/pyitt/actions/workflows/ci.yml/badge.svg)](https://github.com/esuldin/pyitt/actions/workflows/ci.yml)

# pyitt

pyitt is a Python binding to Intel Instrumentation and Tracing Technology (ITT) API. It provides a convenient way
to mark up the Python code for further performance analysis using performance analyzers from Intel like Intel VTune
or others.

pyitt supports following ITT APIs:
 - Collection Control API
 - Counter API
 - Domain API
 - Event API
 - Frame API
 - Id API
 - Processor Trace Control API
 - String Handle API
 - Task API
 - Thread Naming API

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

## Installation

pyitt package is available on [PyPi](https://pypi.org/project/pyitt/) and can be installed in the usual way for the
supported configurations:

    python -m pip install pyitt

## Build

The native part of pyitt module is written using C++20 standard, therefore you need a compiler that supports this
standard, for example GCC-10 for Linux and Visual Studio 2022 for Windows.

### Ubuntu 22.04

1. Install the compiler and Python utilities to build module:

       sudo apt install gcc g++ python3-pip

2. Clone the repository:

       git clone --recurse-submodules https://github.com/esuldin/pyitt.git

3. Build and install pyitt:

       cd pyitt
       python3 -m pip install .

### Windows 10/11

1. Install [Python 3.8+](https://www.python.org/downloads/) together with pip utility.

2. Install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/).
     Make sure that "Desktop development with C++" workload is selected.

3. Clone the repository

       git clone --recurse-submodules https://github.com/esuldin/pyitt.git

4. Build and install pyitt

       cd pyitt
       python -m pip install .


## Compatibility with other Python binding to ITT API

pyitt provides compatibility layers that allow you to use pyitt as a "backend" for other Python bindings to the ITT API.

### [itt-python](https://github.com/NERSC/itt-python)

`pyitt.compatibility_layers.itt_python` fully implements the itt-python public API. It allows you to switch to pyitt
without anything else by only replacing the imports. For example, the following import for itt-python:
 
```python
import itt
```

should be replaced with:

```python
import pyitt.compatibility_layers.itt_python as itt
```

For more details, please see [itt_python_compatibility_sample.py](samples/itt_python_compatibility_sample.py).

### [ittapi](https://github.com/intel/ittapi/)

`pyitt.compatibility_layers.ittapi` implements most of ittapi Python binding public API. Technically, the Python binding
to ITT API that is included in the ITT API repository is based on the pyitt v1.1.0 code base. But, the implementations
have been diverging since then. However, in most cases, it should be possible to use newer versions of pyitt instead of
ittapi just by replacing the imports. For example, the import for ittapi:

```python
import ittapi
```

should be replaced with:

```python
import pyitt.compatibility_layers.ittapi as ittapi
```

## Known Issues and Limitations

- If pyitt is used in a function which is specified as a target for calls from 
  [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) module and an application is profiled on
  Linux with Intel VTune Profiler, the following error may occur:

      <...>/data.0/userapicollector-*.trace' (Data file is corrupted)

  This issue is caused by libittnotify_collector.so library which is a part of Intel VTune Profiler.
  Unfortunately, the issue is not resolvable within pyitt itself. However, a potential workaround is to use 'spawn'
  method for multiprocessing module in the profiled application:

  ```python
  import multiprocessing
  ...
  if __name__ == '__main__':
      multiprocessing.set_start_method('spawn')
  ```
  
  Please see [#1](https://github.com/esuldin/pyitt/issues/1) for more technical information.

## References

 - [Intel® VTune™ Profiler User Guide - Instrumentation and Tracing Technology APIs](https://www.intel.com/content/www/us/en/docs/vtune-profiler/user-guide/2023-0/instrumentation-and-tracing-technology-apis.html)
 - [Intel® VTune™ Profiler User Guide - Task Analysis](https://www.intel.com/content/www/us/en/docs/vtune-profiler/user-guide/2023-0/task-analysis.html)
 - [Intel® VTune™ Profiler Performance Analysis Cookbook - Profiling an Application for Performance Anomalies](https://www.intel.com/content/www/us/en/docs/vtune-profiler/cookbook/2023-1/profiling-performance-anomalies.html/1000.html)
 - [Intel® Graphics Performance Analyzers User Guide - Instrumentation and Tracing Technology API Support](https://www.intel.com/content/www/us/en/docs/gpa/user-guide/2022-4/instrumentation-and-tracing-technology-apis.html)
