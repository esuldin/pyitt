#include "string_handle.hpp"

#include <structmember.h>

#include "extensions/error_template.hpp"
#include "extensions/python.hpp"
#include "extensions/string.hpp"


namespace pyitt
{

static PyObject* string_handle_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
static void string_handle_dealloc(StringHandle* self);

static PyObject* string_handle_repr(StringHandle* self);
static PyObject* string_handle_str(StringHandle* self);

static PyMemberDef string_handle_attrs[] =
{
    {"_str",  T_OBJECT, offsetof(StringHandle, str), READONLY, "a string for which the handle has been created"},
    {nullptr},
};

PyTypeObject StringHandle::object_type =
{
    .ob_base              = PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name              = "pyitt.native.StringHandle",
    .tp_basicsize         = sizeof(StringHandle),
    .tp_itemsize          = 0,

    /* Methods to implement standard operations */
    .tp_dealloc           = reinterpret_cast<destructor>(string_handle_dealloc),
    .tp_vectorcall_offset = 0,
    .tp_getattr           = nullptr,
    .tp_setattr           = nullptr,
    .tp_as_async          = nullptr,
    .tp_repr              = reinterpret_cast<reprfunc>(string_handle_repr),

    /* Method suites for standard classes */
    .tp_as_number         = nullptr,
    .tp_as_sequence       = nullptr,
    .tp_as_mapping        = nullptr,

    /* More standard operations (here for binary compatibility) */
    .tp_hash              = nullptr,
    .tp_call              = nullptr,
    .tp_str               = reinterpret_cast<reprfunc>(string_handle_str),
    .tp_getattro          = nullptr,
    .tp_setattro          = nullptr,

    /* Functions to access object as input/output buffer */
    .tp_as_buffer         = nullptr,

    /* Flags to define presence of optional/expanded features */
    .tp_flags             = Py_TPFLAGS_DEFAULT,

    /* Documentation string */
    .tp_doc               = "A class that represents an ITT string handle.",

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
    .tp_members           = string_handle_attrs,
    .tp_getset            = nullptr,

    /* Strong reference on a heap type, borrowed reference on a static type */
    .tp_base              = nullptr,
    .tp_dict              = nullptr,
    .tp_descr_get         = nullptr,
    .tp_descr_set         = nullptr,
    .tp_dictoffset        = 0,
    .tp_init              = nullptr,
    .tp_alloc             = nullptr,
    .tp_new               = string_handle_new,

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

static PyObject* string_handle_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    pyext::pyobject_holder<StringHandle> self = type->tp_alloc(type, 0);
    if (self == nullptr)
    {
        return nullptr;
    }

    self->str = nullptr;
    self->handle = nullptr;

    char str_key[] = { "str" };
    char* kwlist[] = { str_key, nullptr };

    PyObject* str = nullptr;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O", kwlist, &str))
    {
        return nullptr;
    }

    if (str && PyUnicode_Check(str))
    {
        self->str = pyext::new_ref(str);
    }
    else
    {
        return PyErr_Format(PyExc_TypeError, pyext::error::invalid_argument_type_tmpl, "string", "str");
    }

    pyext::string str_wrapper = pyext::string::from_unicode(self->str);
    if (str_wrapper.c_str() == nullptr)
    {
        return nullptr;
    }

#if defined(_WIN32)
    self->handle = __itt_string_handle_createW(str_wrapper.c_str());
#else
    self->handle = __itt_string_handle_create(str_wrapper.c_str());
#endif

    return self.release();
}

static void string_handle_dealloc(StringHandle* self)
{
    Py_XDECREF(self->str);
    Py_TYPE(self)->tp_free(self);
}

static PyObject* string_handle_repr(StringHandle* self)
{
    return PyUnicode_FromFormat("%s('%U')", self->object_type.tp_name, self->str);
}

static PyObject* string_handle_str(StringHandle* self)
{
    return pyext::new_ref(self->str);
}

int exec_string_handle(PyObject* module)
{
    return pyext::add_type(module, &StringHandle::object_type);
}

}
