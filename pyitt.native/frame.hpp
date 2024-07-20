#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>


namespace pyitt
{

PyObject* frame_begin(PyObject* self, PyObject* args);
PyObject* frame_end(PyObject* self, PyObject* args);

} // namespace pyitt
