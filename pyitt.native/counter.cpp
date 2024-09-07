#include "counter.hpp"

#include <structmember.h>

#include "domain.hpp"
#include "string_handle.hpp"

#include "extensions/error_template.hpp"
#include "extensions/python.hpp"
#include "extensions/string.hpp"


namespace pyitt
{

static PyObject* counter_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
static void counter_dealloc(PyObject* self);

static PyObject* counter_repr(PyObject* self);
static PyObject* counter_str(PyObject* self);

static PyObject* counter_inc(PyObject* self, PyObject* args);
static PyObject* counter_dec(PyObject* self, PyObject* args);
static PyObject* counter_set(PyObject* self, PyObject* arg);

static PyObject* counter_inplace_inc(PyObject* self, PyObject* arg);
static PyObject* counter_inplace_dec(PyObject* self, PyObject* arg);

static PyObject* counter_inc_internal(Counter* self, PyObject* arg);
static PyObject* counter_dec_internal(Counter* self, PyObject* arg);
static PyObject* counter_set_internal(Counter* self, PyObject* arg);

static PyObject* cast_to_pylong(PyObject* obj);

static PyMemberDef counter_attrs[] =
{
    {"domain",  T_OBJECT_EX, offsetof(Counter, domain), READONLY, "a domain that controls the creation and destruction of the counter"},
    {"name",    T_OBJECT_EX, offsetof(Counter, name),   READONLY, "a counter name"},
    {"value",   T_OBJECT_EX, offsetof(Counter, value),  READONLY, "a counter value"},
    {nullptr},
};

static PyMethodDef counter_methods[] =
{
    {"inc", counter_inc, METH_VARARGS, "Increment the counter value."},
    {"dec", counter_dec, METH_VARARGS, "Decrement the counter value."},
    {"set", counter_set, METH_O,       "Set the counter value."},
    {nullptr},
};

static PyNumberMethods counter_number_protocol =
{
    .nb_add = nullptr,
    .nb_subtract = nullptr,
    .nb_multiply = nullptr,
    .nb_remainder = nullptr,
    .nb_divmod = nullptr,
    .nb_power = nullptr,
    .nb_negative = nullptr,
    .nb_positive = nullptr,
    .nb_absolute = nullptr,
    .nb_bool = nullptr,
    .nb_invert = nullptr,
    .nb_lshift = nullptr,
    .nb_rshift = nullptr,
    .nb_and = nullptr,
    .nb_xor = nullptr,
    .nb_or = nullptr,
    .nb_int = nullptr,
    .nb_reserved = nullptr,  /* the slot formerly known as nb_long */
    .nb_float = nullptr,

    .nb_inplace_add = counter_inplace_inc,
    .nb_inplace_subtract = counter_inplace_dec,
    .nb_inplace_multiply = nullptr,
    .nb_inplace_remainder = nullptr,
    .nb_inplace_power = nullptr,
    .nb_inplace_lshift = nullptr,
    .nb_inplace_rshift = nullptr,
    .nb_inplace_and = nullptr,
    .nb_inplace_xor = nullptr,
    .nb_inplace_or = nullptr,

    .nb_floor_divide = nullptr,
    .nb_true_divide = nullptr,
    .nb_inplace_floor_divide = nullptr,
    .nb_inplace_true_divide = nullptr,

    .nb_index = nullptr,

    .nb_matrix_multiply = nullptr,
    .nb_inplace_matrix_multiply = nullptr,
};

PyTypeObject Counter::object_type =
{
    .ob_base              = PyVarObject_HEAD_INIT(nullptr, 0)
    .tp_name              = "pyitt.native.Counter",
    .tp_basicsize         = sizeof(Counter),
    .tp_itemsize          = 0,

    /* Methods to implement standard operations */
    .tp_dealloc           = counter_dealloc,
    .tp_vectorcall_offset = 0,
    .tp_getattr           = nullptr,
    .tp_setattr           = nullptr,
    .tp_as_async          = nullptr,
    .tp_repr              = counter_repr,

    /* Method suites for standard classes */
    .tp_as_number         = &counter_number_protocol,
    .tp_as_sequence       = nullptr,
    .tp_as_mapping        = nullptr,

    /* More standard operations (here for binary compatibility) */
    .tp_hash              = nullptr,
    .tp_call              = nullptr,
    .tp_str               = counter_str,
    .tp_getattro          = nullptr,
    .tp_setattro          = nullptr,

    /* Functions to access object as input/output buffer */
    .tp_as_buffer         = nullptr,

    /* Flags to define presence of optional/expanded features */
    .tp_flags             = Py_TPFLAGS_DEFAULT,

    /* Documentation string */
    .tp_doc               = "A class that represents an ITT counter.",

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
    .tp_methods           = counter_methods,
    .tp_members           = counter_attrs,
    .tp_getset            = nullptr,

    /* Strong reference on a heap type, borrowed reference on a static type */
    .tp_base              = nullptr,
    .tp_dict              = nullptr,
    .tp_descr_get         = nullptr,
    .tp_descr_set         = nullptr,
    .tp_dictoffset        = 0,
    .tp_init              = nullptr,
    .tp_alloc             = nullptr,
    .tp_new               = counter_new,

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

static PyObject* counter_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    pyext::pyobject_holder<Counter> self = type->tp_alloc(type, 0);
    if (self == nullptr)
    {
        return nullptr;
    }

    self->name = nullptr;
    self->domain = nullptr;
    self->value = nullptr;
    self->handle = nullptr;

    char name_key[] = { "name" };
    char domain_key[] = { "domain" };
    char init_value_key[] = { "value" };

    char* kwlist[] = { name_key, domain_key, init_value_key, nullptr };

    PyObject* name = nullptr;
    PyObject* domain = nullptr;
    PyObject* init_value = nullptr;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|OO", kwlist, &name, &domain, &init_value))
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

    if (pyext::pyobject_cast<Domain>(domain))
    {
        self->domain = pyext::xnew_ref(domain);
    }
    else
    {
        PyObject* const domain_type = reinterpret_cast<PyObject*>(&Domain::object_type);

        if (domain == nullptr)
        {
            self->domain = PyObject_CallObject(domain_type, nullptr);
        }
        else
        {
            pyext::pyobject_holder<PyObject> ctor_args = PyTuple_Pack(1, domain);
            if (ctor_args == nullptr)
            {
                return nullptr;
            }

            self->domain = PyObject_CallObject(domain_type, ctor_args.get());
        }
    }

    auto domain_obj = pyext::pyobject_cast<Domain>(self->domain);
    if (self->domain == nullptr)
    {
        return pyext::error::format_from_cause(PyExc_ValueError, "The %s object cannot be created for the instance of %s.",
            Domain::object_type.tp_name, Counter::object_type.tp_name);
    }

    pyext::pyobject_holder<PyObject> zero = PyLong_FromLong(0);
    if (zero == nullptr)
    {
        return nullptr;
    }

    if (init_value == nullptr || init_value == Py_None)
    {
        self->value = pyext::new_ref(zero.get());
    }
    else
    {
        self->value = pyext::xnew_ref(cast_to_pylong(init_value));
    }

    if (self->value == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            "The passed %s is not a valid instance of int and cannot be converted to int.", init_value_key);
    }

    pyext::string name_str = pyext::string::from_unicode(self->name);
    if (name_str.c_str() == nullptr)
    {
        return nullptr;
    }

    pyext::string domain_str = pyext::string::from_unicode(domain_get_name(domain_obj));
    if (domain_str.c_str() == nullptr)
    {
        return nullptr;
    }

    unsigned long long native_init_value = PyLong_AsUnsignedLongLong(self->value);
    if (PyErr_Occurred())
    {
        return nullptr;
    }

#if defined(_WIN32)
    self->handle = __itt_counter_createW(name_str.c_str(), domain_str.c_str());
#else
    self->handle = __itt_counter_create(name_str.c_str(), domain_str.c_str());
#endif

    __itt_counter_set_value(self->handle, &native_init_value);

    return self.release();
}

static void counter_dealloc(PyObject* self)
{
    Counter* obj = pyext::pyobject_cast<Counter>(self);
    if (obj)
    {
        if (obj->handle)
        {
            __itt_counter_destroy(obj->handle);
        }

        Py_XDECREF(obj->name);
        Py_XDECREF(obj->domain);
        Py_XDECREF(obj->value);
    }

    Py_TYPE(self)->tp_free(self);
}

static PyObject* counter_repr(PyObject* self)
{
    Counter* obj = pyext::pyobject_cast<Counter>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Counter::object_type.tp_name);
    }

    return PyUnicode_FromFormat("%s(%R, %R, %R)", obj->object_type.tp_name, obj->name, obj->domain, obj->value);
}

static PyObject* counter_str(PyObject* self)
{
    Counter* obj = pyext::pyobject_cast<Counter>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Counter::object_type.tp_name);
    }

    return PyUnicode_FromFormat("{ name: '%S', domain: '%S', value: %S }", obj->name, obj->domain, obj->value);
}

static PyObject* counter_inc(PyObject* self, PyObject* args)
{
    Counter* obj = pyext::pyobject_cast<Counter>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Counter::object_type.tp_name);
    }

    PyObject* delta = nullptr;
    if (!PyArg_ParseTuple(args, "|O", &delta))
    {
        return nullptr;
    }

    pyext::pyobject_holder<PyObject> delta_value = (delta == nullptr)
        ? PyLong_FromLong(1)
        : pyext::xnew_ref(delta);

    return counter_inc_internal(obj, delta_value.get());
}

static PyObject* counter_dec(PyObject* self, PyObject* args)
{
    Counter* obj = pyext::pyobject_cast<Counter>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Counter::object_type.tp_name);
    }

    PyObject* delta = nullptr;
    if (!PyArg_ParseTuple(args, "|O", &delta))
    {
        return nullptr;
    }

    pyext::pyobject_holder<PyObject> delta_value = (delta == nullptr)
        ? PyLong_FromLong(1)
        : pyext::xnew_ref(delta);

    return counter_dec_internal(obj, delta_value.get());
}

static PyObject* counter_set(PyObject* self, PyObject* arg)
{
    Counter* obj = pyext::pyobject_cast<Counter>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Counter::object_type.tp_name);
    }

    return counter_set_internal(obj, arg);
}

static PyObject* counter_inplace_inc(PyObject* self, PyObject* arg)
{
    Counter* obj = pyext::pyobject_cast<Counter>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Counter::object_type.tp_name);
    }

    if (counter_inc_internal(obj, arg) == nullptr)
    {
        return nullptr;
    }

    return pyext::new_ref(reinterpret_cast<PyObject*>(self));
}

static PyObject* counter_inplace_dec(PyObject* self, PyObject* arg)
{
    Counter* obj = pyext::pyobject_cast<Counter>(self);
    if (obj == nullptr)
    {
        return PyErr_Format(PyExc_TypeError,
            pyext::error::invalid_argument_type_tmpl, "object", Counter::object_type.tp_name);
    }

    if (counter_dec_internal(obj, arg) == nullptr)
    {
        return nullptr;
    }

    return pyext::new_ref(reinterpret_cast<PyObject*>(self));
}

static PyObject* counter_inc_internal(Counter* self, PyObject* arg)
{
    pyext::pyobject_holder<PyObject> delta = cast_to_pylong(arg);
    if (delta == nullptr)
    {
        return PyErr_Format(PyExc_ValueError,
            "The passed delta is not a valid instance of int and cannot be converted to int.");
    }

    pyext::pyobject_holder<PyObject> new_value = PyNumber_Add(self->value, delta.get());
    if (new_value == nullptr)
    {
        return nullptr;
    }

    return counter_set_internal(self, new_value.get());
}

static PyObject* counter_dec_internal(Counter* self, PyObject* arg)
{
    pyext::pyobject_holder<PyObject> delta = cast_to_pylong(arg);
    if (delta == nullptr)
    {
        return PyErr_Format(PyExc_ValueError,
            "The passed delta is not a valid instance of int and cannot be converted to int.");
    }

    pyext::pyobject_holder<PyObject> new_value = PyNumber_Subtract(self->value, delta.get());
    if (new_value == nullptr)
    {
        return nullptr;
    }

    return counter_set_internal(self, new_value.get());
}

static PyObject* counter_set_internal(Counter* self, PyObject* arg)
{
    pyext::pyobject_holder<PyObject> new_value = cast_to_pylong(arg);
    if (new_value == nullptr)
    {
        return PyErr_Format(PyExc_ValueError,
            "The passed value is not a valid instance of int and cannot be converted to int.");
    }

    unsigned long long native_new_value = PyLong_AsUnsignedLongLong(new_value.get());
    if (PyErr_Occurred())
    {
        return nullptr;
    }

    Py_XDECREF(self->value);
    self->value = new_value.release();

    __itt_counter_set_value(self->handle, &native_new_value);

    Py_RETURN_NONE;
}

static PyObject* cast_to_pylong(PyObject* obj)
{
    if (obj == nullptr || PyLong_Check(obj))
    {
        return pyext::xnew_ref(obj);
    }

    PyNumberMethods* nb = Py_TYPE(obj)->tp_as_number;
    if (nb && nb->nb_int)
    {
        PyObject* int_obj = nb->nb_int(obj);
        pyext::error::clear_error_indicator();

        return int_obj;
    }

    return nullptr;
}

int exec_counter(PyObject* module)
{
    return pyext::add_type(module, &Counter::object_type);
}

} // namespace pyitt
