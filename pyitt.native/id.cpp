#include "id.hpp"

#include <structmember.h>

#include <format>

#include "domain.hpp"
#include "string-utilities.hpp"


namespace pyitt
{

template<typename T>
T* id_cast(Id* self);

template<>
PyObject* id_cast(Id* self)
{
    return reinterpret_cast<PyObject*>(self);
}

#define PYITT_ID_TYPE_NAME "pyitt.native.Id"
#define PYITT_ID_TYPE_DOCSTRING "A class that represents a ITT id."

static PyObject* id_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
static void id_dealloc(PyObject* self);

static PyObject* id_repr(PyObject* self);
static PyObject* id_str(PyObject* self);

static PyMemberDef id_attrs[] =
{
    {"domain",  T_OBJECT_EX, offsetof(Id, domain), READONLY, "a domain that controls the creation and destruction of the identifier"},
    {nullptr},
};

PyTypeObject IdType =
{
    .ob_base              = PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name              = PYITT_ID_TYPE_NAME,
    .tp_basicsize         = sizeof(Id),
    .tp_itemsize          = 0,

    /* Methods to implement standard operations */
    .tp_dealloc           = id_dealloc,
    .tp_vectorcall_offset = 0,
    .tp_getattr           = nullptr,
    .tp_setattr           = nullptr,
    .tp_as_async          = nullptr,
    .tp_repr              = id_repr,

    /* Method suites for standard classes */
    .tp_as_number         = nullptr,
    .tp_as_sequence       = nullptr,
    .tp_as_mapping        = nullptr,

    /* More standard operations (here for binary compatibility) */
    .tp_hash              = nullptr,
    .tp_call              = nullptr,
    .tp_str               = id_str,
    .tp_getattro          = nullptr,
    .tp_setattro          = nullptr,

    /* Functions to access object as input/output buffer */
    .tp_as_buffer         = nullptr,

    /* Flags to define presence of optional/expanded features */
    .tp_flags             = Py_TPFLAGS_DEFAULT,

    /* Documentation string */
    .tp_doc               = PYITT_ID_TYPE_DOCSTRING,

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
    Id* self = id_obj(type->tp_alloc(type, 0));

    if (self == nullptr)
    {
        return nullptr;
    }

    char domain_key[] = { "domain" };
    char* kwlist[] = { domain_key, nullptr };

    PyObject* domain = nullptr;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", kwlist, &domain))
    {
        return nullptr;
    }

    if (Py_TYPE(domain) != &DomainType)
    {
        Py_DecRef(id_cast<PyObject>(self));

        PyErr_SetString(PyExc_TypeError, "The passed domain is not a valid instance of Domain type.");
        return nullptr;
    }

    self->domain = pyext::new_ref(domain);
    self->id = __itt_id_make(self, 0);

    __itt_id_create(domain_obj(self->domain)->handle, self->id);

    return id_cast<PyObject>(self);
}

static void id_dealloc(PyObject* self)
{
    if (self == nullptr)
    {
        return;
    }

    Id* obj = id_obj(self);
    if (obj->domain)
    {
        __itt_id_destroy(domain_obj(obj->domain)->handle, obj->id);
    }

    Py_XDECREF(obj->domain);
}

static PyObject* id_repr(PyObject* self)
{
    if (self == nullptr || Py_TYPE(self) != &DomainType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed id is not a valid instance of Id type.");
        return nullptr;
    }

    Id* obj = id_obj(self);
    std::wstring repr = std::format(L"{}({}, {})", PYITT_WSTR(PYITT_ID_TYPE_NAME), obj->id.d1, obj->id.d2);

    return PyUnicode_FromWideChar(repr.c_str(), repr.size());
}

static PyObject* id_str(PyObject* self)
{
    if (self == nullptr || Py_TYPE(self) != &DomainType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed id is not a valid instance of Id type.");
        return nullptr;
    }

    Id* obj = id_obj(self);
    std::string repr = std::format("({}, {})", obj->id.d1, obj->id.d2);

    return PyUnicode_FromStringAndSize(repr.c_str(), repr.size());
}

int exec_id(PyObject* module)
{
    return pyext::add_type(module, &IdType);
}

} // namespace pyitt
