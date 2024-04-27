#include "task.hpp"

#include <ittnotify.h>

#include "domain.hpp"
#include "id.hpp"
#include "string_handle.hpp"

#include "extensions/error_template.hpp"
#include "extensions/python.hpp"


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

    Domain* domain_obj = pyext::pyobject_cast<Domain>(domain);
    if (domain_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "domain", Domain::object_type.tp_name);
    }

    StringHandle* name_string_handle_obj = pyext::pyobject_cast<StringHandle>(name_string_handle);
    if (name_string_handle_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "name", StringHandle::object_type.tp_name);
    }

    __itt_id id = __itt_null;
    if (task_id && task_id != Py_None)
    {
        Id* task_id_obj = pyext::pyobject_cast<Id>(task_id);
        if (task_id_obj == nullptr)
        {
            return PyErr_Format(PyExc_TypeError,
                pyext::error::invalid_argument_type_tmpl, "id", Id::object_type.tp_name);
        }

        id = id_get_handle(task_id_obj);
    }

    __itt_id p_id = __itt_null;
    if (parent_id && parent_id != Py_None)
    {
        Id* parent_id_obj = pyext::pyobject_cast<Id>(parent_id);
        if (parent_id_obj == nullptr)
        {
            return PyErr_Format(PyExc_TypeError,
                pyext::error::invalid_argument_type_tmpl, "parent_id", Id::object_type.tp_name);
        }

        p_id = id_get_handle(parent_id_obj);
    }

    __itt_task_begin(domain_get_handle(domain_obj), id, p_id, string_handle_get_handle(name_string_handle_obj));

    Py_RETURN_NONE;
}

PyObject* task_end(PyObject* self, PyObject* args)
{

    PyObject* domain = nullptr;

    if (!PyArg_ParseTuple(args, "O", &domain))
    {
        return nullptr;
    }

    Domain* domain_obj = pyext::pyobject_cast<Domain>(domain);
    if (domain_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "domain", Domain::object_type.tp_name);
    }

    __itt_task_end(domain_get_handle(domain_obj));

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

    Domain* domain_obj = pyext::pyobject_cast<Domain>(domain);
    if (domain_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "domain", Domain::object_type.tp_name);
    }

    StringHandle* name_string_handle_obj = pyext::pyobject_cast<StringHandle>(name_string_handle);
    if (name_string_handle_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "name", StringHandle::object_type.tp_name);
    }

    Id* task_id_obj = pyext::pyobject_cast<Id>(task_id);
    if (task_id_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "id", Id::object_type.tp_name);
    }

    __itt_id p_id = __itt_null;
    if (parent_id && parent_id != Py_None)
    {
        Id* parent_id_obj = pyext::pyobject_cast<Id>(parent_id);
        if (parent_id_obj == nullptr)
        {
            return PyErr_Format(PyExc_TypeError,
                pyext::error::invalid_argument_type_tmpl, "parent_id", Id::object_type.tp_name);
        }

        p_id = id_get_handle(parent_id_obj);
    }

    __itt_task_begin_overlapped(domain_get_handle(domain_obj),
                                id_get_handle(task_id_obj),
                                p_id,
                                string_handle_get_handle(name_string_handle_obj));

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

    Domain* domain_obj = pyext::pyobject_cast<Domain>(domain);
    if (domain_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "domain", Domain::object_type.tp_name);
    }

    Id* task_id_obj = pyext::pyobject_cast<Id>(task_id);
    if (task_id_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "id", Id::object_type.tp_name);
    }

    __itt_task_end_overlapped(domain_get_handle(domain_obj), id_get_handle(task_id_obj));

    Py_RETURN_NONE;
}

} // namespace pyitt