#include "pt_region.hpp"

#include <structmember.h>

#include "string_handle.hpp"

#include "extensions/error_template.hpp"
#include "extensions/string.hpp"


namespace pyitt
{

static PyObject* pt_region_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
static void pt_region_dealloc(PTRegion* self);

static PyObject* pt_region_repr(PTRegion* self);
static PyObject* pt_region_str(PTRegion* self);

static PyObject* pt_region_begin(PTRegion* self, PyObject* Py_UNUSED(args));
static PyObject* pt_region_end(PTRegion* self, PyObject* Py_UNUSED(args));

#if !defined(ITT_API_IPT_SUPPORT)
static PyObject* pt_region_not_implemented_exception();
#endif

static PyMemberDef pt_region_attrs[] =
{
    {"name",  T_OBJECT, offsetof(PTRegion, name), READONLY, "a PT region name"},
    {nullptr},
};

static PyMethodDef pt_region_methods[] =
{
    {"begin", reinterpret_cast<PyCFunction>(pt_region_begin), METH_NOARGS, "Marks the beginning of a code region targeted for Intel PT analysis."},
    {"end", reinterpret_cast<PyCFunction>(pt_region_end), METH_NOARGS, "Marks the end of a code region targeted for Intel PT analysis."},
    {nullptr}
};

PyTypeObject PTRegion::object_type =
{
    .ob_base              = PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name              = "pyitt.native.PTRegion",
    .tp_basicsize         = sizeof(PTRegion),
    .tp_itemsize          = 0,

    /* Methods to implement standard operations */
    .tp_dealloc           = reinterpret_cast<destructor>(pt_region_dealloc),
    .tp_vectorcall_offset = 0,
    .tp_getattr           = nullptr,
    .tp_setattr           = nullptr,
    .tp_as_async          = nullptr,
    .tp_repr              = reinterpret_cast<reprfunc>(pt_region_repr),

    /* Method suites for standard classes */
    .tp_as_number         = nullptr,
    .tp_as_sequence       = nullptr,
    .tp_as_mapping        = nullptr,

    /* More standard operations (here for binary compatibility) */
    .tp_hash              = nullptr,
    .tp_call              = nullptr,
    .tp_str               = reinterpret_cast<reprfunc>(pt_region_str),
    .tp_getattro          = nullptr,
    .tp_setattro          = nullptr,

    /* Functions to access object as input/output buffer */
    .tp_as_buffer         = nullptr,

    /* Flags to define presence of optional/expanded features */
    .tp_flags             = Py_TPFLAGS_DEFAULT,

    /* Documentation string */
    .tp_doc               = "A class that represents an ITT PT region.",

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
    .tp_methods           = pt_region_methods,
    .tp_members           = pt_region_attrs,
    .tp_getset            = nullptr,

    /* Strong reference on a heap type, borrowed reference on a static type */
    .tp_base              = nullptr,
    .tp_dict              = nullptr,
    .tp_descr_get         = nullptr,
    .tp_descr_set         = nullptr,
    .tp_dictoffset        = 0,
    .tp_init              = nullptr,
    .tp_alloc             = nullptr,
    .tp_new               = pt_region_new,

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

static PyObject* pt_region_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
#if defined(ITT_API_IPT_SUPPORT)
    pyext::pyobject_holder<PTRegion> self = type->tp_alloc(type, 0);
    if (self == nullptr)
    {
        return nullptr;
    }

    self->name = nullptr;
    self->handle = 0;

    char name_key[] = { "name" };
    char* kwlist[] = { name_key, nullptr };

    PyObject* name = nullptr;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O", kwlist, &name))
    {
        return nullptr;
    }

    if (name == nullptr || name == Py_None)
    {
        self->name = pyext::new_ref(Py_None);
    }
    else if (name && PyUnicode_Check(name))
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

    pyext::string name_str;
    if (self->name != Py_None)
    {
        name_str = pyext::string::from_unicode(self->name);
        if (name_str.c_str() == nullptr)
        {
            return nullptr;
        }
    }

# if defined(_WIN32)
    self->handle = __itt_pt_region_createW(name_str.c_str());
# else
    self->handle = __itt_pt_region_create(name_str.c_str());
# endif

    return self.release();
#else
    return pt_region_not_implemented_exception();
#endif
}

static void pt_region_dealloc(PTRegion* self)
{
    Py_XDECREF(self->name);
    Py_TYPE(self)->tp_free(self);
}

static PyObject* pt_region_repr(PTRegion* self)
{
    return PyUnicode_FromFormat("%s('%U')", Py_TYPE(self)->tp_name, self->name);
}

static PyObject* pt_region_str(PTRegion* self)
{
    return pyext::new_ref(self->name);
}

static PyObject* pt_region_begin(PTRegion* self, PyObject* Py_UNUSED(args))
{
#if defined(ITT_API_IPT_SUPPORT)
    __itt_mark_pt_region_begin(self->handle);
    Py_RETURN_NONE;
#else
    return pt_region_not_implemented_exception();
#endif
}

static PyObject* pt_region_end(PTRegion* self, PyObject* Py_UNUSED(args))
{
#if defined(ITT_API_IPT_SUPPORT)
    __itt_mark_pt_region_end(self->handle);
    Py_RETURN_NONE;
#else
    return pt_region_not_implemented_exception();
#endif
}

#if !defined(ITT_API_IPT_SUPPORT)
static PyObject* pt_region_not_implemented_exception()
{
    PyErr_SetString(PyExc_NotImplementedError, "pyitt.native is built without ITT PT API support.");
    return nullptr;
}
#endif

int exec_pt_region(PyObject* module)
{
    return pyext::add_type(module, &PTRegion::object_type);
}

} // namespace pyitt