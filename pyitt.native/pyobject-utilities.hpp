#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <algorithm>

class pyobject_holder
{
public:
	inline pyobject_holder(PyObject* obj);
	inline pyobject_holder(const pyobject_holder& obj);
	inline pyobject_holder(pyobject_holder&& obj);
	inline ~pyobject_holder();

	inline pyobject_holder& operator=(const pyobject_holder&);
	inline pyobject_holder& operator=(pyobject_holder&&);

	inline PyObject* native_object() const;

private:
	PyObject* m_obj;
};

pyobject_holder::pyobject_holder(PyObject* obj)
	: m_obj(obj)
{
	Py_XINCREF(m_obj);
}

pyobject_holder::pyobject_holder(const pyobject_holder& oth)
	: m_obj(oth.m_obj)
{
	Py_XINCREF(m_obj);
}

pyobject_holder::pyobject_holder(pyobject_holder&& oth)
{
	std::swap(m_obj, oth.m_obj);
}

pyobject_holder::~pyobject_holder()
{
	Py_XDECREF(m_obj);
}

pyobject_holder& pyobject_holder::operator=(const pyobject_holder& rhs)
{
	Py_XDECREF(m_obj);
	m_obj = rhs.m_obj;
	Py_XINCREF(m_obj);
	return *this;
}

pyobject_holder& pyobject_holder::operator=(pyobject_holder&& rhs)
{
	std::swap(m_obj, rhs.m_obj);
	return *this;
}

PyObject* pyobject_holder::native_object() const
{
	return m_obj;
}
