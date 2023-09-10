#include "domain.hpp"

#include <structmember.h>

#include <format>

#include "string-utilities.hpp"


namespace pyitt
{

template<typename T>
T* domain_cast(Domain* self);

template<>
PyObject* domain_cast(Domain* self)
{
    return reinterpret_cast<PyObject*>(self);
}

#define PYITT_DOMAIN_TYPE_NAME "pyitt.native.Domain"
#define PYITT_DOMAIN_TYPE_DOCSTRING "A class that represents a ITT domain."

static PyObject* domain_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
static void domain_dealloc(PyObject* self);

static PyObject* domain_repr(PyObject* self);
static PyObject* domain_str(PyObject* self);

static PyMemberDef domain_attrs[] =
{
    {"name",  T_OBJECT, offsetof(Domain, name), READONLY, "a domain name"},
    {nullptr},
};

PyTypeObject DomainType =
{
    .ob_base              = PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name              = PYITT_DOMAIN_TYPE_NAME,
    .tp_basicsize         = sizeof(Domain),
    .tp_itemsize          = 0,

    /* Methods to implement standard operations */
    .tp_dealloc           = domain_dealloc,
    .tp_vectorcall_offset = 0,
    .tp_getattr           = nullptr,
    .tp_setattr           = nullptr,
    .tp_as_async          = nullptr,
    .tp_repr              = domain_repr,

    /* Method suites for standard classes */
    .tp_as_number         = nullptr,
    .tp_as_sequence       = nullptr,
    .tp_as_mapping        = nullptr,

    /* More standard operations (here for binary compatibility) */
    .tp_hash              = nullptr,
    .tp_call              = nullptr,
    .tp_str               = domain_str,
    .tp_getattro          = nullptr,
    .tp_setattro          = nullptr,

    /* Functions to access object as input/output buffer */
    .tp_as_buffer         = nullptr,

    /* Flags to define presence of optional/expanded features */
    .tp_flags             = Py_TPFLAGS_DEFAULT,

    /* Documentation string */
    .tp_doc               = PYITT_DOMAIN_TYPE_DOCSTRING,

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
    Domain* self = domain_obj(type->tp_alloc(type, 0));
    if (self == nullptr)
    {
        return nullptr;
    }

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
    else
    {
        Py_DecRef(domain_cast<PyObject>(self));

        PyErr_SetString(PyExc_TypeError, "The passed domain name is not a valid instance of str.");
        return nullptr;
    }

#if defined(_WIN32)
    wchar_t* name_wstr = PyUnicode_AsWideCharString(self->name, nullptr);
    if (name_wstr == nullptr)
    {
        Py_DecRef(domain_cast<PyObject>(self));
        return nullptr;
    }

    self->handle = __itt_domain_createW(name_wstr);
    PyMem_Free(name_wstr);
#else
    const char* name_str = PyUnicode_AsUTF8(self->name);
    if (name_str == nullptr)
    {
        Py_DecRef(domain_cast<PyObject>(self));
        return nullptr;
    }

    self->handle = __itt_domain_create(name_str);
#endif

    return domain_cast<PyObject>(self);
}

static void domain_dealloc(PyObject* self)
{
    if (self == nullptr)
    {
        return;
    }

    Domain* obj = domain_obj(self);
    Py_XDECREF(obj->name);
}

static PyObject* domain_repr(PyObject* self)
{
    if (self == nullptr || Py_TYPE(self) != &DomainType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed domain is not a valid instance of Domain type.");
        return nullptr;
    }

    Domain* obj = domain_obj(self);
    if (obj->name == nullptr)
    {
        PyErr_SetString(PyExc_AttributeError, "The name attribute has not been initialized.");
        return nullptr;
    }

    Py_ssize_t name_size = 0;
    wchar_t* name = PyUnicode_AsWideCharString(obj->name, &name_size);
    if (name == nullptr)
    {
        return nullptr;
    }

    std::wstring repr = std::format(L"{}('{}')", PYITT_WSTR(PYITT_DOMAIN_TYPE_NAME), name);
    PyMem_Free(name);

    return PyUnicode_FromWideChar(repr.c_str(), repr.size());
}

static PyObject* domain_str(PyObject* self)
{
    if (self == nullptr || Py_TYPE(self) != &DomainType)
    {
        PyErr_SetString(PyExc_TypeError, "The passed domain is not a valid instance of Domain type.");
        return nullptr;
    }

    Domain* obj = domain_obj(self);
    if (obj->name == nullptr)
    {
        PyErr_SetString(PyExc_AttributeError, "The name attribute has not been initialized.");
        return nullptr;
    }

    return pyext::new_ref(obj->name);
}

int exec_domain(PyObject* module)
{
    return pyext::add_type(module, &DomainType);
}

} // namespace pyitt
