#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <ittnotify.h>

#include "extensions/python.hpp"


namespace pyitt
{

struct PTRegion
{
	PyObject_HEAD
	PyObject* name;
	__itt_pt_region handle;

	static PyTypeObject object_type;
};

int exec_pt_region(PyObject* module);

} // namespace pyitt
