#include "task.hpp"

#include <ittnotify.h>

#include "domain.hpp"
#include "id.hpp"
#include "string_handle.hpp"

namespace pyitt
{

PyObject* task_begin(PyObject* self, PyObject* args)
{
    PyObject* domain = nullptr;
    PyObject* name_string_handle = nullptr;
    PyObject* task_id = nullptr;
    PyObject* parent_id = nullptr;

    if (!PyArg_ParseTuple(args, "OO|OO", &domain, &name_string_handle, &task_id, &parent_id))
    {
        return nullptr;
    }

    if (Py_TYPE(domain) != &DomainType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed domain object is not a valid instance of Domain type.");
        return nullptr;
    }

    if (Py_TYPE(name_string_handle) != &StringHandleType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed task name object is not a valid instance of StringHandle type.");
        return nullptr;
    }

    __itt_id id = __itt_null;
    if (task_id && task_id != Py_None)
    {
        if (Py_TYPE(task_id) != &IdType)
        {
            PyErr_SetString(PyExc_TypeError, "The passed task id object is not a valid instance of Id type.");
            return nullptr;
        }

        id = id_obj(task_id)->id;
    }

    __itt_id p_id = __itt_null;
    if (parent_id && parent_id != Py_None)
    {
        if (Py_TYPE(parent_id) != &IdType)
        {
            PyErr_SetString(PyExc_TypeError, "The passed parent id object is not a valid instance of Id type.");
            return nullptr;
        }

        p_id = id_obj(parent_id)->id;
    }

    __itt_task_begin(domain_obj(domain)->handle, id, p_id, string_handle_obj(name_string_handle)->handle);

    Py_RETURN_NONE;
}

PyObject* task_end(PyObject* self, PyObject* args)
{

    PyObject* domain = nullptr;

    if (!PyArg_ParseTuple(args, "O", &domain))
    {
        return nullptr;
    }

    if (Py_TYPE(domain) != &DomainType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed domain object is not a valid instance of Domain type.");
        return nullptr;
    }

    __itt_task_end(domain_obj(domain)->handle);

    Py_RETURN_NONE;
}

PyObject* task_begin_overlapped(PyObject* self, PyObject* args)
{
    PyObject* domain = nullptr;
    PyObject* name_string_handle = nullptr;
    PyObject* task_id = nullptr;
    PyObject* parent_id = nullptr;

    if (!PyArg_ParseTuple(args, "OOO|O", &domain, &name_string_handle, &task_id, &parent_id))
    {
        return nullptr;
    }

    if (Py_TYPE(domain) != &DomainType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed domain object is not a valid instance of Domain type.");
        return nullptr;
    }

    if (Py_TYPE(name_string_handle) != &StringHandleType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed task name object is not a valid instance of StringHandle type.");
        return nullptr;
    }


    if (Py_TYPE(task_id) != &IdType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed task id object is not a valid instance of Id type.");
        return nullptr;
    }

    __itt_id p_id = __itt_null;
    if (parent_id && parent_id != Py_None)
    {
        if (Py_TYPE(parent_id) != &IdType)
        {
            PyErr_SetString(PyExc_TypeError, "The passed parent id object is not a valid instance of Id type.");
            return nullptr;
        }

        p_id = id_obj(parent_id)->id;
    }

    __itt_task_begin_overlapped(domain_obj(domain)->handle,
                                id_obj(task_id)->id,
                                p_id,
                                string_handle_obj(name_string_handle)->handle);

    Py_RETURN_NONE;
}

PyObject* task_end_overlapped(PyObject* self, PyObject* args)
{

    PyObject* domain = nullptr;
    PyObject* task_id = nullptr;

    if (!PyArg_ParseTuple(args, "OO", &domain, &task_id))
    {
        return nullptr;
    }

    if (Py_TYPE(domain) != &DomainType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed domain object is not a valid instance of Domain type.");
        return nullptr;
    }

    if (Py_TYPE(task_id) != &IdType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed task id object is not a valid instance of Id type.");
        return nullptr;
    }

    __itt_task_end_overlapped(domain_obj(domain)->handle, id_obj(task_id)->id);

    Py_RETURN_NONE;
}

} // namespace pyitt