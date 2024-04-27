#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <type_traits>
#include <utility>


namespace pyitt
{
namespace pyext
{

template<typename T>
T* pyobject_cast(PyObject* self)
{
	return reinterpret_cast<T*>(self && Py_TYPE(self) == &(T::object_type) ? self : nullptr);
}

template<>
inline PyObject* pyobject_cast(PyObject* self)
{
	return self;
}

inline PyObject* new_ref(PyObject* obj);
inline PyObject* xnew_ref(PyObject* obj);

int add_type(PyObject* module, PyTypeObject* type);

/* Implementation of inline functions */
PyObject* new_ref(PyObject* obj)
{
	Py_INCREF(obj);
	return obj;
}

PyObject* xnew_ref(PyObject* obj)
{
	Py_XINCREF(obj);
	return obj;
}

template<typename T>
class pyobject_holder
{
public:
	pyobject_holder()
		: m_object(nullptr)
	{}

	pyobject_holder(PyObject* obj)
		: m_object(obj)
	{}

	pyobject_holder(const pyobject_holder& oth)
		: m_object(xnew_ref(oth.m_object))
	{}

	pyobject_holder(pyobject_holder&& oth)
		: m_object(std::exchange(oth.m_object, nullptr))
	{}

	~pyobject_holder()
	{
		Py_XDECREF(m_object);
	}

	pyobject_holder& operator=(const pyobject_holder& rhs)
	{
		Py_XDECREF(m_object);
		m_object = xnew_ref(rhs.m_object);

		return *this;
	}

	pyobject_holder& operator=(pyobject_holder&& rhs)
	{
		std::swap(m_object, rhs.m_object);
		return *this;
	}

	bool operator==(std::nullptr_t) const
	{
		return std::is_same<T, PyObject>::value
			? m_object == nullptr
			: pyobject_cast<T>(m_object) == nullptr;
	}

	PyObject* get() const
	{
		return m_object;
	}

	PyObject* release()
	{
		PyObject* tmp_obj = m_object;
		m_object = nullptr;

		return tmp_obj;
	}

	T* operator->()
	{
		return pyobject_cast<T>(m_object);
	}

	const T* operator->() const
	{
		return pyobject_cast<T>(m_object);
	}

private:
	PyObject* m_object;
};

} // namespace pyext
} // namespace pyitt
