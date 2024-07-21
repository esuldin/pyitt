#include "id.hpp"

#include <structmember.h>

#include "domain.hpp"

#include "extensions/error_template.hpp"
#include "extensions/python.hpp"
#include "extensions/string.hpp"

#include <cstring>


namespace pyitt
{

static PyObject* id_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
static void id_dealloc(Id* self);

static PyObject* id_repr(Id* self);
static PyObject* id_str(Id* self);

static PyMemberDef id_attrs[] =
{
    {"domain",  T_OBJECT_EX, offsetof(Id, domain), READONLY, "a domain that controls the creation and destruction of the identifier"},
    {nullptr},
};

PyTypeObject Id::object_type =
{
    .ob_base              = PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name              = "pyitt.native.Id",
    .tp_basicsize         = sizeof(Id),
    .tp_itemsize          = 0,

    /* Methods to implement standard operations */
    .tp_dealloc           = reinterpret_cast<destructor>(id_dealloc),
    .tp_vectorcall_offset = 0,
    .tp_getattr           = nullptr,
    .tp_setattr           = nullptr,
    .tp_as_async          = nullptr,
    .tp_repr              = reinterpret_cast<reprfunc>(id_repr),

    /* Method suites for standard classes */
    .tp_as_number         = nullptr,
    .tp_as_sequence       = nullptr,
    .tp_as_mapping        = nullptr,

    /* More standard operations (here for binary compatibility) */
    .tp_hash              = nullptr,
    .tp_call              = nullptr,
    .tp_str               = reinterpret_cast<reprfunc>(id_str),
    .tp_getattro          = nullptr,
    .tp_setattro          = nullptr,

    /* Functions to access object as input/output buffer */
    .tp_as_buffer         = nullptr,

    /* Flags to define presence of optional/expanded features */
    .tp_flags             = Py_TPFLAGS_DEFAULT,

    /* Documentation string */
    .tp_doc               = "A class that represents an ITT id.",

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
    .tp_members           = id_attrs,
    .tp_getset            = nullptr,

    /* Strong reference on a heap type, borrowed reference on a static type */
    .tp_base              = nullptr,
    .tp_dict              = nullptr,
    .tp_descr_get         = nullptr,
    .tp_descr_set         = nullptr,
    .tp_dictoffset        = 0,
    .tp_init              = nullptr,
    .tp_alloc             = nullptr,
    .tp_new               = id_new,

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

static PyObject* id_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    pyext::pyobject_holder<Id> self = type->tp_alloc(type, 0);
    if (self == nullptr)
    {
        return nullptr;
    }

    self->domain = nullptr;
    self->handle = __itt_null;

    char domain_key[] = { "domain" };
    char* kwlist[] = { domain_key, nullptr };

    PyObject* domain = nullptr;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", kwlist, &domain))
    {
        return nullptr;
    }

    Domain* domain_obj = pyext::pyobject_cast<Domain>(domain);
    if (domain_obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, domain_key, Domain::object_type.tp_name);
    }

    self->domain = pyext::new_ref(domain);
    self->handle = __itt_id_make(self.get(), 0);

    __itt_id_create(domain_get_handle(domain_obj), self->handle);

    return self.release();
}

static void id_dealloc(Id* self)
{
    Domain* domain_obj = pyext::pyobject_cast<Domain>(self->domain);
    if (domain_obj && std::memcmp(&(self->handle), &(__itt_null), sizeof(self->handle)))
    {
        __itt_id_destroy(domain_get_handle(domain_obj), self->handle);
    }

    Py_XDECREF(self->domain);
    Py_TYPE(self)->tp_free(self);
}

static PyObject* id_repr(Id* self)
{
    return PyUnicode_FromFormat("%s(%llu, %llu)", self->object_type.tp_name, self->handle.d1, self->handle.d2);
}

static PyObject* id_str(Id* self)
{
    return PyUnicode_FromFormat("(%llu, %llu)", self->handle.d1, self->handle.d2);
}

int exec_id(PyObject* module)
{
    return pyext::add_type(module, &Id::object_type);
}

} // namespace pyitt
