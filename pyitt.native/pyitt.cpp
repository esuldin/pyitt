#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "pyitt_exec.hpp"


PyMODINIT_FUNC PyInit_native()
{
    return pyitt::init_pyitt_module();
}
