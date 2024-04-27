#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <ittnotify.h>


namespace pyitt
{

struct Event
{
	PyObject_HEAD
	PyObject* name;
	__itt_event handle;

	static PyTypeObject object_type;
};


int exec_event(PyObject* module);

} // namespace pyitt
