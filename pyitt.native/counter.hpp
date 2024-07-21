#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <ittnotify.h>


namespace pyitt
{

struct Counter
{
	PyObject_HEAD
	PyObject* name;
	PyObject* value;
	PyObject* domain;
	__itt_counter handle;

	static PyTypeObject object_type;
};

int exec_counter(PyObject* module);

} // namespace pyitt
