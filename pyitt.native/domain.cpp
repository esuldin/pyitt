#include "domain.hpp"

#include <structmember.h>

#include "string_handle.hpp"

#include "extensions/error_template.hpp"
#include "extensions/python.hpp"
#include "extensions/string.hpp"


namespace pyitt
{

static PyObject* domain_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
static void domain_dealloc(Domain* self);

static PyObject* domain_repr(Domain* self);
static PyObject* domain_str(Domain* self);

static PyMemberDef domain_attrs[] =
{
    {"name",  T_OBJECT, offsetof(Domain, name), READONLY, "a domain name"},
    {nullptr},
};

PyTypeObject Domain::object_type =
{
    .ob_base              = PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name              = "pyitt.native.Domain",
    .tp_basicsize         = sizeof(Domain),
    .tp_itemsize          = 0,

    /* Methods to implement standard operations */
    .tp_dealloc           = reinterpret_cast<destructor>(domain_dealloc),
    .tp_vectorcall_offset = 0,
    .tp_getattr           = nullptr,
    .tp_setattr           = nullptr,
    .tp_as_async          = nullptr,
    .tp_repr              = reinterpret_cast<reprfunc>(domain_repr),

    /* Method suites for standard classes */
    .tp_as_number         = nullptr,
    .tp_as_sequence       = nullptr,
    .tp_as_mapping        = nullptr,

    /* More standard operations (here for binary compatibility) */
    .tp_hash              = nullptr,
    .tp_call              = nullptr,
    .tp_str               = reinterpret_cast<reprfunc>(domain_str),
    .tp_getattro          = nullptr,
    .tp_setattro          = nullptr,

    /* Functions to access object as input/output buffer */
    .tp_as_buffer         = nullptr,

    /* Flags to define presence of optional/expanded features */
    .tp_flags             = Py_TPFLAGS_DEFAULT,

    /* Documentation string */
    .tp_doc               = "A class that represents an ITT domain.",

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
    .tp_methods           = nullptr,
    .tp_members           = domain_attrs,
    .tp_getset            = nullptr,

    /* Strong reference on a heap type, borrowed reference on a static type */
    .tp_base              = nullptr,
    .tp_dict              = nullptr,
    .tp_descr_get         = nullptr,
    .tp_descr_set         = nullptr,
    .tp_dictoffset        = 0,
    .tp_init              = nullptr,
    .tp_alloc             = nullptr,
    .tp_new               = domain_new,

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

static PyObject* domain_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    pyext::pyobject_holder<Domain> self = type->tp_alloc(type, 0);
    if (self == nullptr)
    {
        return nullptr;
    }

    self->handle = nullptr;
    self->name = nullptr;

    char name_key[] = { "name" };
    char* kwlist[] = { name_key, nullptr };

    PyObject* name = nullptr;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O", kwlist, &name))
    {
        return nullptr;
    }

    if (name == nullptr || name == Py_None)
    {
        self->name = PyUnicode_FromString("pyitt");
    }
    else if (PyUnicode_Check(name))
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
    self->handle = __itt_domain_createW(name_str.c_str());
#else
    self->handle = __itt_domain_create(name_str.c_str());
#endif

    return self.release();
}

static void domain_dealloc(Domain* self)
{
    Py_XDECREF(self->name);
    Py_TYPE(self)->tp_free(self);
}

static PyObject* domain_repr(Domain* self)
{
    return PyUnicode_FromFormat("%s('%U')", Py_TYPE(self)->tp_name, self->name);
}

static PyObject* domain_str(Domain* self)
{
    return pyext::new_ref(self->name);
}

int exec_domain(PyObject* module)
{
    return pyext::add_type(module, &Domain::object_type);
}

} // namespace pyitt
