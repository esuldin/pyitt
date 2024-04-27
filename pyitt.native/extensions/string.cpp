#include "string.hpp"

#include <algorithm>


namespace pyitt
{
namespace pyext
{

string::string(string&& oth) noexcept
	: m_str(oth.m_str)
	, m_is_owner(oth.m_is_owner)
{
	oth.m_str = nullptr;
	oth.m_is_owner = false;
}

string& string::operator=(string&& rhs) noexcept
{
	std::swap(m_str, rhs.m_str);
	std::swap(m_is_owner, rhs.m_is_owner);

	return *this;
}

void string::deallocate() noexcept
{
	if (m_is_owner)
	{
		PyMem_Free(const_cast<pointer>(m_str));
	}
}

string string::from_unicode(PyObject* str) noexcept
{
	if (!PyUnicode_Check(str))
	{
		return string(nullptr, false);
	}

#if defined(_WIN32)
	pointer str_ptr = PyUnicode_AsWideCharString(str, nullptr);
	const bool is_owner = true;
#else
	const_pointer str_ptr = PyUnicode_AsUTF8(str);
	const bool is_owner = false;
#endif

	return string(str_ptr, is_owner);
}

}
}
