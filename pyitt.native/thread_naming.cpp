#include "collection_control.hpp"

#include <ittnotify.h>

#include "string_handle.hpp"


#include "extensions/error_template.hpp"
#include "extensions/python.hpp"
#include "extensions/string.hpp"


namespace pyitt
{

PyObject* thread_set_name(PyObject* Py_UNUSED(self), PyObject* name)
{
    if (auto string_handle_obj = pyext::pyobject_cast<StringHandle>(name))
    {
        PyObject* string_handle_str = string_handle_get_string(string_handle_obj);
        if (string_handle_str == nullptr)
        {
            return PyErr_Format(PyExc_ValueError,
                "Passed %s object as name does not hold string.", StringHandle::object_type.tp_name);
        }

        name = pyext::new_ref(string_handle_str);
    }
    else if (!PyUnicode_Check(name))
    {
        return PyErr_Format(PyExc_TypeError,
            "The passed name is not a valid instance of str or %s.", StringHandle::object_type.tp_name);
    }

    pyext::string name_str = pyext::string::from_unicode(name);
    if (name_str.c_str() == nullptr)
    {
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