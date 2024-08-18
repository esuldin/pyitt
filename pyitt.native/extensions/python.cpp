#include "python.hpp"


namespace pyitt
{
namespace pyext
{

int add_type(PyObject* module, PyTypeObject* type)
{
	if (PyType_Ready(type) < 0)
	{
		return -1;
	}

	const char* name = _PyType_Name(type);

	Py_INCREF(type);
	return PyModule_AddObject(module, name, _PyObject_CAST(type));
}

namespace error
{

PyObject* get_raised_exception()
{
#if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 12
    pyobject_holder<PyObject> type;
    pyobject_holder<PyObject> value;
    pyobject_holder<PyObject> traceback;

    PyErr_Fetch(&(type.get()), &(value.get()), &(traceback.get()));

    if (type == nullptr && value == nullptr && traceback == nullptr)
    {
        return nullptr;
    }

    PyErr_NormalizeException(&(type.get()), &(value.get()), &(traceback.get()));
    if (traceback != nullptr)
    {
        PyException_SetTraceback(value.get(), traceback.release());
    }

    return value.release();
#else
    return PyErr_GetRaisedException();
#endif
}

void set_raised_exception(PyObject* exception)
{
#if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 12
    PyErr_Restore(
        xnew_ref(reinterpret_cast<PyObject*>(Py_TYPE(exception))),
        exception,
        PyException_GetTraceback(exception));
#else
    PyErr_SetRaisedException(exception);
#endif
}

void clear_error_indicator()
{
#if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION < 12
    PyObject* type = nullptr;
    PyObject* value = nullptr;
    PyObject* traceback = nullptr;

    PyErr_Fetch(&type, &value, &traceback);

    Py_XDECREF(type);
    Py_XDECREF(value);
    Py_XDECREF(traceback);
#else
    PyObject* exception = PyErr_GetRaisedException();
    Py_XDECREF(exception);
#endif
}

PyObject* format_from_cause(PyObject* exception_type, const char* format, ...)
{
    va_list vargs;
    va_start(vargs, format);
    format_from_cause(exception_type, format, vargs);
    va_end(vargs);

    return nullptr;
}

PyObject* format_from_cause(PyObject* exception_type, const char* format, va_list vargs)
{
    pyobject_holder<PyObject> raised_exception = get_raised_exception();

    PyErr_FormatV(exception_type, format, vargs);

    pyobject_holder<PyObject> current_exception = get_raised_exception();
    if (raised_exception != nullptr)
    {
        PyException_SetCause(current_exception.get(), new_ref(raised_exception.get()));
        PyException_SetContext(current_exception.get(), new_ref(raised_exception.get()));
    }
    set_raised_exception(current_exception.release());

    return nullptr;
}

}

} // namespace pyext
} // namespace pyitt
