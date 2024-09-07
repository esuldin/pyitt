#include "event.hpp"

#include <structmember.h>

#include "string_handle.hpp"

#include "extensions/error_template.hpp"
#include "extensions/python.hpp"
#include "extensions/string.hpp"


namespace pyitt
{

static PyObject* event_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
static void event_dealloc(PyObject* self);

static PyObject* event_repr(PyObject* self);
static PyObject* event_str(PyObject* self);

static PyObject* event_begin(PyObject* self, PyObject* Py_UNUSED(args));
static PyObject* event_end(PyObject* self, PyObject* Py_UNUSED(args));

static PyMemberDef event_attrs[] =
{
    {"name",  T_OBJECT_EX, offsetof(Event, name), READONLY, "a name of the event"},
    {nullptr},
};

static PyMethodDef event_methods[] =
{
    {"begin", event_begin, METH_NOARGS, "Marks the beginning of the event."},
    {"end", event_end, METH_NOARGS, "Marks the end of the event."},
    {nullptr},
};

PyTypeObject Event::object_type =
{
    .ob_base              = PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name              = "pyitt.native.Event",
    .tp_basicsize         = sizeof(Event),
    .tp_itemsize          = 0,

    /* Methods to implement standard operations */
    .tp_dealloc           = event_dealloc,
    .tp_vectorcall_offset = 0,
    .tp_getattr           = nullptr,
    .tp_setattr           = nullptr,
    .tp_as_async          = nullptr,
    .tp_repr              = event_repr,

    /* Method suites for standard classes */
    .tp_as_number         = nullptr,
    .tp_as_sequence       = nullptr,
    .tp_as_mapping        = nullptr,

    /* More standard operations (here for binary compatibility) */
    .tp_hash              = nullptr,
    .tp_call              = nullptr,
    .tp_str               = event_str,
    .tp_getattro          = nullptr,
    .tp_setattro          = nullptr,

    /* Functions to access object as input/output buffer */
    .tp_as_buffer         = nullptr,

    /* Flags to define presence of optional/expanded features */
    .tp_flags             = Py_TPFLAGS_DEFAULT,

    /* Documentation string */
    .tp_doc               = "A class that represents an ITT event.",

    /* Assigned meaning in release 2.0 call function for all accessible objects */
    .tp_traverse          = nullptr,

    /* Delete references to contained objects */
    .tp_clear             = nullptr,

    /* Assigned meaning in release 2.1 rich comparisons */
    .tp_richcompare       = nullptr,

    /* weak reference enabler */
    .tp_weaklistoffset    = 0,

    /* Iterators */
    .tp_iter              = nullptr,
    .tp_iternext          = nullptr,

    /* Attribute descriptor and subclassing stuff */
    .tp_methods           = event_methods,
    .tp_members           = event_attrs,
    .tp_getset            = nullptr,

    /* Strong reference on a heap type, borrowed reference on a static type */
    .tp_base              = nullptr,
    .tp_dict              = nullptr,
    .tp_descr_get         = nullptr,
    .tp_descr_set         = nullptr,
    .tp_dictoffset        = 0,
    .tp_init              = nullptr,
    .tp_alloc             = nullptr,
    .tp_new               = event_new,

    /* Low-level free-memory routine */
    .tp_free              = nullptr,

    /* For PyObject_IS_GC */
    .tp_is_gc             = nullptr,
    .tp_bases             = nullptr,

    /* method resolution order */
    .tp_mro               = nullptr,
    .tp_cache             = nullptr,
    .tp_subclasses        = nullptr,
    .tp_weaklist          = nullptr,
    .tp_del               = nullptr,

    /* Type attribute cache version tag. Added in version 2.6 */
    .tp_version_tag       = 0,

    .tp_finalize          = nullptr,
    .tp_vectorcall        = nullptr,
};

static PyObject* event_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    pyext::pyobject_holder<Event> self = type->tp_alloc(type, 0);
    if (self == nullptr)
    {
        return nullptr;
    }

    self->name = nullptr;
    self->handle = 0;

    char name_key[] = { "name" };
    char* kwlist[] = { name_key, nullptr };

    PyObject* name = nullptr;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", kwlist, &name))
    {
        return nullptr;
    }

    if (name && PyUnicode_Check(name))
    {
        self->name = pyext::new_ref(name);
    }
    else if (auto string_handle_obj = pyext::pyobject_cast<StringHandle>(name))
    {
        self->name = pyext::xnew_ref(string_handle_get_string(string_handle_obj));
    }
    else
    {
        return PyErr_Format(PyExc_TypeError,
            "The passed %s is not a valid instance of str or %s.", name_key, StringHandle::object_type.tp_name);
    }

    pyext::string name_str = pyext::string::from_unicode(self->name);
    if (name_str.c_str() == nullptr)
    {
        return nullptr;
    }

#if defined(_WIN32)
    self->handle = __itt_event_createW(name_str.c_str(), static_cast<int>(name_str.length()));
#else
    self->handle = __itt_event_create(name_str.c_str(), static_cast<int>(name_str.length()));
#endif

    return self.release();
}

static void event_dealloc(PyObject* self)
{
    Event* obj = pyext::pyobject_cast<Event>(self);
    if (obj)
    {
        Py_XDECREF(obj->name);
    }

    Py_TYPE(self)->tp_free(self);
}

static PyObject* event_repr(PyObject* self)
{
    Event* obj = pyext::pyobject_cast<Event>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Event::object_type.tp_name);
    }

    return PyUnicode_FromFormat("%s('%U')", obj->object_type.tp_name, obj->name);
}

static PyObject* event_str(PyObject* self)
{
    Event* obj = pyext::pyobject_cast<Event>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Event::object_type.tp_name);
    }

    return pyext::new_ref(obj->name);
}

static PyObject* event_begin(PyObject* self, PyObject* Py_UNUSED(args))
{
    Event* obj = pyext::pyobject_cast<Event>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Event::object_type.tp_name);
    }

    __itt_event_start(obj->handle);
    Py_RETURN_NONE;
}

static PyObject* event_end(PyObject* self, PyObject* Py_UNUSED(args))
{
    Event* obj = pyext::pyobject_cast<Event>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Event::object_type.tp_name);
    }

    __itt_event_end(obj->handle);
    Py_RETURN_NONE;
}

int exec_event(PyObject* module)
{
    return pyext::add_type(module, &Event::object_type);
}

} // namespace pyitt
