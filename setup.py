"""
setup.py - Python module to install pyitt package
"""
import os
import platform
import sys
import sysconfig

from setuptools import find_namespace_packages, setup, Extension
from setuptools.command.build_ext import build_ext
from subprocess import run  # pylint: disable=C0411


def get_environment_flag(name):
    """
    Get an environment variable and check its value.
    :param name: the environment variable name
    :return: None if the environment variable is not set. False if the environment variable is set and has one of the
             following values: `''`, `0`, `n`, `no` or `false`. Otherwise, return True.
    """
    flag_value = os.environ.get(name, None)
    return (flag_value and flag_value.lower() not in ('0', 'n', 'no', 'false')) if flag_value is not None else None


IS_64_ARCHITECTURE = sys.maxsize > 2 ** 32

# Check if custom location for ITT API source code is specified
ITT_DEFAULT_DIR = 'ittapi'
itt_dir = os.environ.get('PYITT_ITT_API_SOURCE_DIR', None)
itt_dir = itt_dir if itt_dir else ITT_DEFAULT_DIR

assert os.path.exists(itt_dir), 'The specified directory with ITT API source code does not exist.'
assert itt_dir != ITT_DEFAULT_DIR or len(os.listdir(itt_dir)), \
    (f'The specified directory with ITT API source code ({itt_dir}) is empty.\n'
     f'Make sure that submodules are checked out as well using following command:\n'
     f'git submodule update --init --recursive')


# Check if IPT support is requested
def is_x86_arch():
    """Returns true if the machine has x86 compatible architecture."""
    return platform.machine() in ['i386', 'i486', 'i586', 'i686', 'x86', 'x86_64', 'AMD64']


build_itt_with_ipt_support = get_environment_flag('PYITT_BUILD_WITH_ITT_API_IPT_SUPPORT')
build_itt_with_ipt_support = build_itt_with_ipt_support if build_itt_with_ipt_support is not None else is_x86_arch()

itt_source = [os.path.join(itt_dir, 'src', 'ittnotify', 'ittnotify_static.c')]
itt_include_dirs = [os.path.join(itt_dir, 'include')]
itt_license_files = [f'{itt_dir}/LICENSES/BSD-3-Clause.txt'] if itt_dir == ITT_DEFAULT_DIR else []

if build_itt_with_ipt_support:
    itt_compiler_flags = ['-DITT_API_IPT_SUPPORT']
    if sys.platform == 'win32':
        ITT_PTMARK_SOURCE = 'ittptmark64.asm' if IS_64_ARCHITECTURE else 'ittptmark32.asm'
    else:
        ITT_PTMARK_SOURCE = 'ittptmark64.S' if IS_64_ARCHITECTURE else 'ittptmark32.S'
    itt_extra_objects = [os.path.join(itt_dir, 'src', 'ittnotify', ITT_PTMARK_SOURCE)]
else:
    itt_compiler_flags = []
    itt_extra_objects = []

pyitt_license_files = ['LICENSE']
pyitt_native_sources = ['pyitt.native/extensions/python.cpp',
                        'pyitt.native/extensions/string.cpp',
                        'pyitt.native/collection_control.cpp',
                        'pyitt.native/counter.cpp',
                        'pyitt.native/domain.cpp',
                        'pyitt.native/event.cpp',
                        'pyitt.native/frame.cpp',
                        'pyitt.native/id.cpp',
                        'pyitt.native/pt_region.cpp',
                        'pyitt.native/string_handle.cpp',
                        'pyitt.native/task.cpp',
                        'pyitt.native/thread_naming.cpp',
                        'pyitt.native/pyitt_exec.cpp',
                        'pyitt.native/pyitt.cpp']

pyitt_native_compiler_args = ['/std:c++20' if sys.platform == 'win32' else '-std=c++20']
pyitt_native_link_args = []

# Check if code coverage is requested
build_with_code_coverage = get_environment_flag('PYITT_NATIVE_BUILD_WITH_CODE_COVERAGE')
build_with_code_coverage = build_with_code_coverage if build_with_code_coverage is not None else False

if build_with_code_coverage:
    assert build_with_code_coverage and sys.platform != 'win32', 'Build with code coverage is not supported on Windows.'
    pyitt_native_compiler_args.append('--coverage')
    pyitt_native_link_args.append('--coverage')

# Workaround for issue #283 in distutils (formerly #4571 in setuptools)
if sys.platform != 'win32':
    LDSHARED_VAR_NAME = 'LDSHARED'
    LDCXXSHARED_VAR_NAME = 'LDCXXSHARED'

    if LDCXXSHARED_VAR_NAME not in sysconfig.get_config_vars() and LDCXXSHARED_VAR_NAME not in os.environ:
        if LDSHARED_VAR_NAME in os.environ:
            os.environ[LDCXXSHARED_VAR_NAME] = os.environ[LDSHARED_VAR_NAME]
        else:
            os.environ[LDCXXSHARED_VAR_NAME] = sysconfig.get_config_vars().get(LDSHARED_VAR_NAME, None)

pyitt_native = Extension('pyitt.native',
                         sources=itt_source + pyitt_native_sources,
                         include_dirs=itt_include_dirs,
                         extra_compile_args=itt_compiler_flags + pyitt_native_compiler_args,
                         extra_link_args=pyitt_native_link_args,
                         extra_objects=itt_extra_objects)


class NativeBuildExtension(build_ext):  # pylint: disable=R0903
    """
    A class that implements the build extension to compile pyitt.native module.
    """
    def build_extension(self, ext) -> None:
        """
        Build native extension module
        :param ext: the extension to build
        """
        if ext.name == 'pyitt.native' and self.compiler.compiler_type == 'msvc':
            # Setup asm tool
            as_tool = 'ml64.exe' if IS_64_ARCHITECTURE else 'ml.exe'
            as_ext = '.asm'

            if hasattr(self.compiler, 'initialized') and hasattr(self.compiler, 'initialize'):
                if not self.compiler.initialized:
                    self.compiler.initialize()

            as_path = os.path.dirname(self.compiler.cc) if hasattr(self.compiler, 'cc') else ''

            # Extract asm files from extra objects
            # pylint: disable=W0106
            asm_files = [filename for filename in ext.extra_objects if filename.lower().endswith(as_ext)]
            [ext.extra_objects.remove(filename) for filename in asm_files]

            # Create temp directories
            [os.makedirs(os.path.join(self.build_temp, os.path.dirname(filename)), exist_ok=True)
             for filename in asm_files]

            # Generate target names
            src_dir = os.path.dirname(__file__)
            obj_asm_pairs = [(os.path.join(self.build_temp, os.path.splitext(filename)[0]) + '.obj',
                              os.path.join(src_dir, filename)) for filename in asm_files]
            # Compile
            [run([os.path.join(as_path, as_tool), '/Fo', obj_file, '/c', asm_file], check=True)
             for obj_file, asm_file in obj_asm_pairs]

            [ext.extra_objects.append(obj_file) for obj_file, _ in obj_asm_pairs]

        build_ext.build_extension(self, ext)


setup(packages=find_namespace_packages(include=['pyitt', 'pyitt.*']),
      ext_modules=[pyitt_native],
      license_files=pyitt_license_files + itt_license_files,
      cmdclass={'build_ext': NativeBuildExtension} if build_itt_with_ipt_support else {},
      zip_safe=False)
