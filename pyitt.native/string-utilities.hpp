#pragma once

#define PYITT_CONCAT(p, v) p##v
#define PYITT_WSTR(s) PYITT_CONCAT(L, s)
