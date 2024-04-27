#pragma once

namespace pyitt
{
namespace pyext
{
namespace error
{

inline constexpr const char* attribute_not_initilized_tmpl = "The %s attribute has not been initialized.";
inline constexpr const char* bad_alloc_tmpl = "Cannot allocate the %s object.";
inline constexpr const char* invalid_argument_type_tmpl = "The passed %s is not a valid instance of %s type.";
inline constexpr const char* invalid_argument_value_tmpl = "The value of %s argument is not valid.";

}
}
}