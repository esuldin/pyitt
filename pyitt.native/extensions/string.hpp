#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#if defined(_WIN32)
#include <cwchar>
#else
#include <cstring>
#endif


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

    inline string() noexcept;
    string(const string&) = delete;
    inline string(string&& oth) noexcept;
    inline ~string();

    string& operator=(const string&) = delete;
    string& operator=(string&& rhs) noexcept;

    inline const_pointer c_str() const noexcept;
    inline std::size_t length() const noexcept;

	static string from_unicode(PyObject* str) noexcept;

private:
    inline string(const_pointer str, bool take_ownership) noexcept;

    void deallocate() noexcept;

    const_pointer m_str;
    bool m_is_owner;
};

string::string() noexcept
    : string(nullptr, false)
{}

string::string(const_pointer str, bool take_ownership) noexcept
    : m_str(str)
    , m_is_owner(take_ownership)
{}

string::string(string&& oth) noexcept
	: m_str(oth.m_str)
	, m_is_owner(oth.m_is_owner)
{
	oth.m_str = nullptr;
	oth.m_is_owner = false;
}

string::~string()
{
    deallocate();
}

string::const_pointer string::c_str() const noexcept
{
    return m_str;
}

std::size_t string::length() const noexcept
{
    const_pointer str_ptr = c_str();
#if defined(_WIN32)
    return str_ptr ? std::wcslen(str_ptr) : 0;
#else
    return str_ptr ? std::strlen(str_ptr) : 0;
#endif
}

}
}