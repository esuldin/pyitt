#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <ittnotify.h>


namespace pyitt
{

struct StringHandle
{
	PyObject_HEAD
	PyObject* str;
	__itt_string_handle* handle;

	static PyTypeObject object_type;
};

inline __itt_string_handle* string_handle_get_handle(const StringHandle* obj)
{
	return obj ? obj->handle : nullptr;
}

inline PyObject* string_handle_get_string(const StringHandle* obj)
{
	return obj ? obj->str : nullptr;
}

int exec_string_handle(PyObject* module);

} // namespace pyitt
