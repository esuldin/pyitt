#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>


namespace pyitt
{

PyObject* init_pyitt_module();

} // namespace pyitt
