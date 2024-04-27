#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <ittnotify.h>


namespace pyitt
{

struct Id
{
	PyObject_HEAD
	PyObject* domain;
	__itt_id handle;

	static PyTypeObject object_type;
};

inline __itt_id id_get_handle(const Id* obj)
{
	return obj ? obj->handle : __itt_null;
}

int exec_id(PyObject* module);

} // namespace pyitt
