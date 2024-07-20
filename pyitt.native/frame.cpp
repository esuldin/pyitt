#include "frame.hpp"

#include <ittnotify.h>

#include "domain.hpp"
#include "id.hpp"

#include "extensions/error_template.hpp"
#include "extensions/python.hpp"

namespace pyitt
{

PyObject* frame_begin(PyObject* self, PyObject* args)
{
    PyObject* domain = nullptr;
    PyObject* frame_id = nullptr;

    if (!PyArg_ParseTuple(args, "O|O", &domain, &frame_id))
    {
        return nullptr;
    }

    Domain* domain_obj = pyext::pyobject_cast<Domain>(domain);
    if (domain_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "domain", Domain::object_type.tp_name);
    }

    const __itt_id* id = nullptr;
    if (frame_id && frame_id != Py_None)
    {
        Id* frame_id_obj = pyext::pyobject_cast<Id>(frame_id);
        if (frame_id_obj == nullptr)
        {
            return PyErr_Format(PyExc_TypeError,
                pyext::error::invalid_argument_type_tmpl, "id", Id::object_type.tp_name);
        }

        id = &(id_get_handle(frame_id_obj));
    }

    __itt_frame_begin_v3(domain_obj->handle, const_cast<__itt_id*>(id));

    Py_RETURN_NONE;
}

PyObject* frame_end(PyObject* self, PyObject* args)
{

    PyObject* domain = nullptr;
    PyObject* frame_id = nullptr;

    if (!PyArg_ParseTuple(args, "O|O", &domain, &frame_id))
    {
        return nullptr;
    }

    Domain* domain_obj = pyext::pyobject_cast<Domain>(domain);
    if (domain_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "domain", Domain::object_type.tp_name);
    }

    const __itt_id* id = nullptr;
    if (frame_id && frame_id != Py_None)
    {
        Id* frame_id_obj = pyext::pyobject_cast<Id>(frame_id);
        if (frame_id_obj == nullptr)
        {
            return PyErr_Format(PyExc_TypeError,
                pyext::error::invalid_argument_type_tmpl, "id", Id::object_type.tp_name);
        }

        id = &(id_get_handle(frame_id_obj));
    }

    __itt_frame_end_v3(domain_obj->handle, const_cast<__itt_id*>(id));

    Py_RETURN_NONE;
}

} // namespace pyitt
