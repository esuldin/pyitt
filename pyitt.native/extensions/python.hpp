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
#if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 10
	Py_INCREF(obj);
	return obj;
#else
	return Py_NewRef(obj);
#endif
}

PyObject* xnew_ref(PyObject* obj)
{
#if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 10
	Py_XINCREF(obj);
	return obj;
#else
	return Py_XNewRef(obj);
#endif
}

template<typename T>
class pyobject_holder
{
public:
	using pointer = std::add_pointer_t<T>;
	using py_object_pointer = std::add_pointer_t<PyObject>;

	pyobject_holder()
		: m_object(nullptr)
	{}

	pyobject_holder(py_object_pointer obj)
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

	bool operator!=(std::nullptr_t) const
	{
		return !(operator==(nullptr));
	}

	const py_object_pointer& get() const
	{
		return m_object;
	}

	py_object_pointer& get()
	{
		return m_object;
	}

	py_object_pointer release()
	{
		PyObject* tmp_obj = m_object;
		m_object = nullptr;

		return tmp_obj;
	}

	pointer operator->()
	{
		return pyobject_cast<T>(m_object);
	}

	const pointer operator->() const
	{
		return pyobject_cast<T>(m_object);
	}

private:
	PyObject* m_object;
};

namespace error
{

PyObject* get_raised_exception();
void set_raised_exception(PyObject* exception);

void clear_error_indicator();

PyObject* format_from_cause(PyObject* exception, const char* format, ...);
PyObject* format_from_cause(PyObject* exception_type, const char* format, va_list vargs);

} // namespace pyerr

} // namespace pyext
} // namespace pyitt
