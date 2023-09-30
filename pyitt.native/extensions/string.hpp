#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>


namespace pyitt
{
namespace pyext
{

class string
{
public:
#if defined(_WIN32)
	using value_type = wchar_t;
#else
	using value_type = char;
#endif

    using reference = value_type&;
    using const_reference = const value_type&;
    using pointer = value_type*;
    using const_pointer = const value_type*;

    ~string();

    inline const_pointer c_str() const;

	static string from_unicode(PyObject* str);

private:
    inline string(const_pointer str, bool take_ownership);

    const_pointer m_str;
    bool m_is_owner;
};

string::string(const_pointer str, bool take_ownership)
    : m_str(str)
    , m_is_owner(take_ownership)
{}

string::const_pointer string::c_str() const
{
    return m_str;
}

}
}