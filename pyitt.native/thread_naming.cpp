#include "collection_control.hpp"

#include <ittnotify.h>

#include "string_handle.hpp"
#include "extensions/string.hpp"


namespace pyitt
{

PyObject* thread_set_name(PyObject* self, PyObject* name)
{
    if (Py_TYPE(name) == &StringHandleType)
    {
        name = string_handle_obj(name)->str;
    }
    else if (!PyUnicode_Check(name))
    {
        PyErr_SetString(PyExc_TypeError, "The passed thread name is not a valid instance of str or StringHandle.");
        return nullptr;
    }

    pyext::string name_str = pyext::string::from_unicode(name);
    if (name_str.c_str() == nullptr)
    {
        PyErr_SetString(PyExc_RuntimeError, "Cannot convert unicode to native string.");
        return nullptr;
    }

#if defined(_WIN32)
    __itt_thread_set_nameW(name_str.c_str());
#else
    __itt_thread_set_name(name_str.c_str());
#endif

    Py_RETURN_NONE;
}

} // namespace pyitt