import os
import sys

from setuptools import setup, Extension

vtune_dir = os.environ.get('VTUNE_PROFILER_DIR', None)
oneapi_dir = os.environ.get('ONEAPI_ROOT', None)

if vtune_dir is None and oneapi_dir:
    vtune_dir = os.path.join(oneapi_dir, 'vtune', 'latest')

if vtune_dir is None:
    if sys.platform == 'win32':
        default_path = 'C:\\Program Files (x86)\\Intel\\oneAPI\\vtune\\latest'
    else:
        default_path = '/opt/intel/oneapi/vtune/latest'
    if os.path.exists(default_path):
        vtune_dir = default_path

if sys.platform == 'win32':
    amplxe_vars_script_command = '<vtune_install_dir>\\amplxe-vars.bat'
    export_command = 'set VTUNE_PROFILER_DIR=<vtune_install_dir>'
else:
    amplxe_vars_script_command = '<vtune_install_dir>/amplxe-vars.sh'
    export_command = 'export VTUNE_PROFILER_DIR=<vtune_install_dir>'

assert vtune_dir is not None, (f'VTune Profiler installation directory is not specified.\n'
                               f'Use {amplxe_vars_script_command} to prepare the environment or specify VTune Profiler'
                               f' installation directory using VTUNE_PROFILER_DIR environment variable:\n'
                               f'{export_command}')

is_64_architecture = sys.maxsize > 2**32

pyitt_native_sources = ['pyitt.native/python-extensions.cpp',
                        'pyitt.native/collection_control.cpp',
                        'pyitt.native/domain.cpp',
                        'pyitt.native/id.cpp',
                        'pyitt.native/string_handle.cpp',
                        'pyitt.native/task.cpp',
                        'pyitt.native/thread_naming.cpp',
                        'pyitt.native/pyitt.cpp',]
pyitt_native_include_dirs = [os.path.join(vtune_dir, 'include')]
pyitt_native_library_dirs = [os.path.join(vtune_dir, 'lib64' if is_64_architecture else 'lib32')]
pyitt_native_libraries = ['libittnotify'] if sys.platform == 'win32' else ['ittnotify']
pyitt_native_compiler_args = ['/std:c++20'] if sys.platform == 'win32' else ['-std=c++20']

pyitt_native = Extension('pyitt.native', 
                         sources=pyitt_native_sources,
                         libraries=pyitt_native_libraries,
                         include_dirs=pyitt_native_include_dirs,
                         library_dirs=pyitt_native_library_dirs,
                         extra_compile_args=pyitt_native_compiler_args)

setup(name='pyitt',
      version='1.0.0',
      description='ITT API bindings for Python',
      packages=['pyitt'],
      ext_modules=[pyitt_native])
