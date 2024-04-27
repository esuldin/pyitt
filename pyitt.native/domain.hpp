#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <ittnotify.h>


namespace pyitt
{

struct Domain
{
	PyObject_HEAD
	PyObject* name;
	__itt_domain* handle;

	static PyTypeObject object_type;
};

inline __itt_domain* domain_get_handle(const Domain* obj)
{
	return obj ? obj->handle : nullptr;
}

inline PyObject* domain_get_name(const Domain* obj)
{
	return obj ? obj->name : nullptr;
}

int exec_domain(PyObject* module);

} // namespace pyitt
